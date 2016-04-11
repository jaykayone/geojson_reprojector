from pyramid.view import view_config
import requests, pyproj
from pyproj import Proj


p1 = Proj(init="EPSG:2169")
p2 = Proj(init="EPSG:4326")


def __reproject(_p):
    ll = pyproj.transform(p1, p2, _p[0], _p[1])
    _p[0] = round(ll[0], 6)
    _p[1] = round(ll[1], 6)
    return _p

@view_config(route_name='home',renderer="templates/mytemplate.pt")
def home(request):
    describe_url = "http://opendata.vdl.lu/odaweb/index.jsp?describe=1"
    catalog = requests.get(describe_url).json()
    _catalog = []
    for item in catalog["data"]:
        _item = {}
        _item["name"] = item["i18n"]["fr"]["name"]
        _item["id"] = item["id"]
        _catalog.append(_item)

    return {"_catalog" : sorted(_catalog, key=lambda k: k['name'])}

@view_config(route_name='reproject',renderer="json")
def reproject(request):
    url = request.params['url']
    geojson_object = requests.get(url).json()

    if "crs" in geojson_object:
        del geojson_object["crs"]
    for f in geojson_object['features']:
        if "bbox" in f:
            del f["bbox"]
        if f["geometry"]["type"] == "Point":
            if f["geometry"]["coordinates"][0] < 1000:
                continue
            p = f["geometry"]["coordinates"]
            p = __reproject(p)
        if f["geometry"]["type"] == "Polygon":
            print f["geometry"]
            if f["geometry"]["coordinates"][0][0][0] < 1000:
                continue
            for r in f["geometry"]["coordinates"]:
                print r
                for p in r:
                    print p
                    p = __reproject(p)
        else:
            if f["geometry"]["coordinates"][0][0] < 1000:
                continue
            for p in f["geometry"]["coordinates"]:
                p = __reproject(p)
    return geojson_object