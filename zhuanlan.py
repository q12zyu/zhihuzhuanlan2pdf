# -*-coding:utf-8-*-

""" 爬取一个知乎专栏的信息，生成一个专栏封面，并获取专栏中的所有文章
"""

import json
from mako.template import Template
from session import session
from article import Article
import os.path


class ZhuanLan:
    """ 爬取专栏信息和专栏中的所有文章
    """

    def __init__(self, s, slug):
        """ s： 网络访问用的 session
        slug：专栏的唯一名"""

        self.s = s
        self.slug = slug
        self.img_path = './out/img'  # 图片的保存路径
        self.cover_template = Template(filename='./template/cover.html', input_encoding='utf-8')

    def _img_download(self, url):
        """ 下载 url 指定的图片并保存到本地，并返回本地路径"""
        # 提取 url 中图片的名称
        name = url[url.rfind('/')+1:]
        # 如果本地已经有该图片就不再下载，节省时间和流量
        path = self.img_path + '/' + name
        if os.path.isfile(path):
            return './img/' + name
        binary_content = self.s.get(url=url).content
        with open(file=path, mode='wb') as f:
            f.write(binary_content)

        return './img/' + name

    def _get_zhuanlan_info(self):
        """ 爬取专栏信息"""
        url = 'https://zhuanlan.zhihu.com/api/columns/' + self.slug
        json_obj = json.loads(self.s.get(url=url).text, encoding='utf-8')
        # 提取需要的信息
        self.zhuanlan_dict = dict()
        self.zhuanlan_dict['avatar'] = json_obj['avatar']['template'].replace('{id}', json_obj['avatar']['id']).\
            replace('{size}', 'r')
        # 将图片保存到本地
        self.zhuanlan_dict['avatar'] = self._img_download(self.zhuanlan_dict['avatar'])
        self.zhuanlan_dict['name'] = json_obj['name']
        self.name = self.zhuanlan_dict['name']
        self.zhuanlan_dict['intro'] = json_obj['intro']
        self.zhuanlan_dict['followers_count'] = json_obj['followersCount']
        self.zhuanlan_dict['post_count'] = json_obj['postsCount']

        # 话题列表
        self.zhuanlan_dict['post_topics'] = []
        for d in json_obj['postTopics']:
            self.zhuanlan_dict['post_topics'].append({'name': d['name'], 'posts_count': d['postsCount']})

        self.zhuanlan_dict['post_topics'].sort(key=lambda obj: obj['posts_count'], reverse=True)

    def _get_cover(self):
        self._get_zhuanlan_info()
        return self.cover_template.render(zhuanlan_dict=self.zhuanlan_dict).encode('utf-8', 'replace')

    def _get_article_list(self):
        """ 获取该专栏下面的各篇文章的html渲染结果
        """
        article = Article()
        article_list = []
        for i in range(self.zhuanlan_dict['post_count']):
            url = 'https://zhuanlan.zhihu.com/api/columns/{0}/posts?limit=1&offset={1}'.format(self.slug, i)
            article_list.append(article.get_article_html(url=url))

        return article_list

    def get_result(self):
        """ 返回cover 和文章列表"""
        return self._get_cover(), self._get_article_list()


if __name__ == '__main__':
    zhuanlan = ZhuanLan(s=session, slug='auxten')

    with open(file='./out/cover_test.html', mode='wb') as f:
        f.write(zhuanlan._get_cover())
