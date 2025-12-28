# -*- coding: utf-8 -*-
# @Author  : Doubebly
# @Time    : 2025/1/21 23:07

import sys
import sqlite3
import base64
import json
from contextlib import closing

sys.path.append('..')
from base.spider import Spider


class Spider(Spider):
    def getName(self):
        return "LocalDB"

    def init(self, extend):
        # 本地 sqlite 数据库路径
        self.db_path = '/storage/emulated/0/lz/ys.db'
        # t 映射表，与原 PHP 一致
        self.replace_map = {1: 6, 2: 13, 3: 60, 4: 38, 27: 52}

    def getDependence(self):
        return []

    def isVideoFormat(self, url):
        # 这里按框架约定返回 False 即可，由外部判定
        return False

    def manualVideoCheck(self):
        return False

    # ---------- 内部通用工具 ----------

    def _connect_db(self):
        """获取数据库连接，自动设置 row_factory。"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def _safe_int(value, default=None):
        """安全转换为 int，失败返回默认值。"""
        try:
            return int(value)
        except Exception:
            return default

    @staticmethod
    def _like_keyword(keyword: str) -> str:
        """生成 LIKE 查询使用的关键字。"""
        return f"%{keyword}%" if keyword is not None else "%%"

    # ---------- home：分类 ----------

    def homeContent(self, filter):
        categories = [
            {"type_id": "传媒", "type_name": "传媒"},
            {"type_id": "FC2", "type_name": "FC2"},
            {"type_id": "PPV", "type_name": "PPV"},
            {"type_id": "巨乳", "type_name": "巨乳"},
            {"type_id": "人妻", "type_name": "人妻"},
            {"type_id": "美女", "type_name": "美女"},
            {"type_id": "性爱", "type_name": "性爱"},
            {"type_id": "妻子", "type_name": "妻子"},
            {"type_id": "性感", "type_name": "性感"},
            {"type_id": "姐姐", "type_name": "姐姐"},
            {"type_id": "极品", "type_name": "极品"},
            {"type_id": "探花", "type_name": "探花"},
            {"type_id": "女孩", "type_name": "女孩"},
            {"type_id": "女友", "type_name": "女友"},
            {"type_id": "高潮", "type_name": "高潮"},
            {"type_id": "少妇", "type_name": "少妇"},
            {"type_id": "做爱", "type_name": "做爱"},
            {"type_id": "中出", "type_name": "中出"},
            {"type_id": "妹妹", "type_name": "妹妹"},
            {"type_id": "蜜桃", "type_name": "蜜桃"},
            {"type_id": "可爱", "type_name": "可爱"},
            {"type_id": "91", "type_name": "91"},
            {"type_id": "射精", "type_name": "射精"},
            {"type_id": "淫荡", "type_name": "淫荡"},
            {"type_id": "内射", "type_name": "内射"},
            {"type_id": "诱惑", "type_name": "诱惑"},
            {"type_id": "拍摄", "type_name": "拍摄"},
            {"type_id": "少女", "type_name": "少女"},
            {"type_id": "星空", "type_name": "星空"},
            {"type_id": "美少女", "type_name": "美少女"},
            {"type_id": "黑丝", "type_name": "黑丝"},
            {"type_id": "老公", "type_name": "老公"},
            {"type_id": "罩杯", "type_name": "罩杯"},
            {"type_id": "大学生", "type_name": "大学生"},
            {"type_id": "男人", "type_name": "男人"},
            {"type_id": "调教", "type_name": "调教"},
            {"type_id": "一个", "type_name": "一个"},
            {"type_id": "勾引", "type_name": "勾引"},
            {"type_id": "酒店", "type_name": "酒店"},
            {"type_id": "男友", "type_name": "男友"},
            {"type_id": "NTR", "type_name": "NTR"},
            {"type_id": "身材", "type_name": "身材"},
            {"type_id": "爆操", "type_name": "爆操"},
            {"type_id": "学生", "type_name": "学生"},
            {"type_id": "肉棒", "type_name": "肉棒"},
            {"type_id": "无码", "type_name": "无码"},
            {"type_id": "精液", "type_name": "精液"},
            {"type_id": "口交", "type_name": "口交"},
            {"type_id": "女子", "type_name": "女子"},
        ]
        return {'class': categories}

    def homeVideoContent(self):
        # 如需首页推荐，可在此从 DB 中按时间取若干条；目前保持行为：返回空列表
        return {'list': [], 'parse': 0, 'jx': 0}

    # ---------- 分类列表 ----------

    def categoryContent(self, cid, page, filter, ext):
        # ext 优先：如果 ext 是 base64(json) 且有 cid，则覆盖 cid
        if ext:
            try:
                decoded = base64.b64decode(ext).decode('utf-8')
                obj = json.loads(decoded)
                if isinstance(obj, dict) and 'cid' in obj:
                    cid = str(self._safe_int(obj.get('cid'), cid))
            except Exception:
                # ext 异常不影响正常分类
                pass

        # 数字 cid 映射为真实类型 ID
        cid_int = self._safe_int(cid, None)
        if cid_int is not None and cid_int in self.replace_map:
            cid = str(self.replace_map[cid_int])

        # 页码、分页
        page = self._safe_int(page, 1)
        if page is None or page < 1:
            page = 1
        limit = 20
        offset = (page - 1) * limit

        like_kw = self._like_keyword(cid)

        total = 0
        rows = []
        try:
            with closing(self._connect_db()) as conn, closing(conn.cursor()) as cur:
                cur.execute("SELECT COUNT(*) FROM cj WHERE vod_name LIKE ?", (like_kw,))
                total = cur.fetchone()[0] or 0

                cur.execute(
                    "SELECT vod_id, vod_name, vod_pic, vod_remarks "
                    "FROM cj WHERE vod_name LIKE ? LIMIT ? OFFSET ?",
                    (like_kw, limit, offset)
                )
                rows = [dict(r) for r in cur.fetchall()]
        except Exception:
            # 这里也可以写日志，但不抛异常以免中断播放
            rows = []
            total = 0

        pagecount = (total + limit - 1) // limit if limit > 0 else 0

        return {
            'page': page,
            'pagecount': pagecount,
            'limit': limit,
            'total': total,
            'list': rows,
            'parse': 0,
            'jx': 0
        }

    # ---------- 详情 ----------

    def detailContent(self, did):
        # did 一般为列表，取第一项
        if not did:
            return {'list': [], 'parse': 0, 'jx': 0}

        ids = did[0]
        row_dict = None

        try:
            with closing(self._connect_db()) as conn, closing(conn.cursor()) as cur:
                cur.execute("SELECT * FROM cj WHERE vod_id = ?", (ids,))
                row = cur.fetchone()
                if row:
                    row_dict = dict(row)
        except Exception:
            row_dict = None

        if not row_dict:
            return {'list': [], 'parse': 0, 'jx': 0}

        # 不破坏你现有字段：所有表字段原样透传
        data = dict(row_dict)

        # 如后续你表中有专门的播放字段，可以在此补充：
        # data.setdefault('vod_play_from', '本地')
        # data.setdefault('vod_play_url', '')

        return {'list': [data], 'parse': 0, 'jx': 0}

    # ---------- 搜索 ----------

    def searchContent(self, key, quick, page='1'):
        # 按你原来的逻辑：只处理第一页
        if self._safe_int(page, 1) > 1:
            return {'list': [], 'parse': 0, 'jx': 0}

        like_kw = self._like_keyword(key)
        rows = []

        try:
            with closing(self._connect_db()) as conn, closing(conn.cursor()) as cur:
                cur.execute("SELECT * FROM cj WHERE vod_name LIKE ?", (like_kw,))
                rows = [dict(r) for r in cur.fetchall()]
        except Exception:
            rows = []

        total = len(rows)
        return {
            'total': total,
            'limit': total,
            'pagecount': 1,
            'page': 1,
            'list': rows,
            'parse': 0,
            'jx': 0
        }

    # ---------- 播放 ----------

    def playerContent(self, flag, pid, vipFlags):
        """
        你的现有逻辑：pid 即真实播放地址，直出不解析。
        如需接解析，可改为拼接解析接口再设置 parse=1 / jx=1。
        """
        url = pid or ""
        headers = {
            "User-Agent": "okhttp/3.12.0"
        }
        return {
            "url": url,
            "header": headers,
            "parse": 0,
            "jx": 0
        }

    # ---------- 代理 / 销毁 ----------

    def localProxy(self, params):
        # 保持占位实现，便于后续做本地转发
        return [200, "video/MP2T", "", ""]

    def destroy(self):
        return '正在Destroy'


if __name__ == '__main__':
    pass
