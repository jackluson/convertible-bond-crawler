curl -o ./output.html 'https://www.ninwin.cn/index.php?m=cb&a=cb_all&show_cb_only=Y&show_listed_only=Y' \
  -H 'Connection: keep-alive' \
  -H 'Pragma: no-cache' \
  -H 'Cache-Control: no-cache' \
  -H 'sec-ch-ua: " Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "macOS"' \
  -H 'Upgrade-Insecure-Requests: 1' \
  -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36' \
  -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9' \
  -H 'Sec-Fetch-Site: same-origin' \
  -H 'Sec-Fetch-Mode: navigate' \
  -H 'Sec-Fetch-User: ?1' \
  -H 'Sec-Fetch-Dest: document' \
  -H 'Referer: https://www.ninwin.cn/index.php?m=cb&show_cb_only=Y&show_listed_only=Y' \
  -H 'Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.7,en-CA;q=0.6,la;q=0.5' \
  -H 'Cookie: P0s_cbQuestion=1; csrf_token=fa78e4758e83d722; __51cke__=; P0s_Pw_verify_code=rvN6Dc2j3t8%3D; P0s_winduser=CVZKOIYdTmNbQZ1vQCqmx2%2FK0vh%2FIuooz1RGvIgPwJLb6aOdAU57HHOqtko%3D; P0s_visitor=aoQM1Jgm3f5Fo%2BPYcsjC20pId9%2BShHVksbCw1yq0RS33dk%2FrPK3Pyxu%2F2UdLSgjMDZ2NqnGw%2BqZGrHEYoTnq3HgtyVgWhZ9xPwDFFA%3D%3D; PHPSESSID=itfecui449a4b663t8ml5ps7ek; __tins__4771153=%7B%22sid%22%3A%201664376657922%2C%20%22vd%22%3A%207%2C%20%22expires%22%3A%201664378542953%7D; __51laig__=7; P0s_lastvisit=1452%091664376744%09%2Findex.php%3Fm%3DmyAdmin%26c%3Dlog' \
  -H 'charset=UTF-8' \
  | iconv -f utf-8 -t gbk
