#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2020/5/11 11:14
# @Author : way
# @Site : all
# @Describe: 基础类，附件下载

import re
import logging
from scrapy.pipelines.files import FilesPipeline
from scrapy.http import Request
from scrapy.utils.log import failure_to_exc_info

logger = logging.getLogger(__name__)


class FilePipeline(FilesPipeline):

    def get_media_requests(self, item, info):
        if item.get('file_url'):
            meta = {
                'spider': info.spider.name,
                'file_name': re.sub('[:*?"<>|]', '', item['file_name']),
                'file_type': item['file_type']
            }
            yield Request(item['file_url'], meta=meta)

    def file_path(self, request, response=None, info=None):
        spider = request.meta['spider']
        file_name = request.meta['file_name']
        file_type = request.meta['file_type']
        filename = f'{spider}/{file_name}.{file_type}'
        return filename

    def item_completed(self, results, item, info):
        for ok, value in results:
            if ok:
                item['status'] = '下载成功'
                item['file_path'] = self.store.basedir + '/' + value['path']
            else:
                item['status'] = '下载失败'
                item['file_path'] = ''
                logger.error(
                    '%(class)s found errors processing %(item)s',
                    {'class': self.__class__.__name__, 'item': item},
                    exc_info=failure_to_exc_info(value),
                    extra={'spider': info.spider}
                )
        return item
