from posts.models import PostLocale, Post
from bs4 import BeautifulSoup
import json
def change_status_wordpress(post_slug, status):
    import requests
    url_srcdest = 'https://activities.afinidata.com/wp-json/wp/v2/posts'
    user = 'estuar.diaz'
    password = '28rS Y9U3 z51d I1E3 0Fng zTsY'
    headers = {'Content-Type': 'application/json',
               'Authorization': 'Basic %s' % (password),
               'Username': 'estuar.diaz',
               'Password': '%s' % (password)}
    data = {
        'slug': post_slug,
        'status': 'draft'
    }
    r = requests.get(url_srcdest, data=json.dumps(data), headers=headers, auth=(user, password))
    id = None
    try:
        id = r.json()[0]['id']
    except:
        data = \
            {
                "slug": post_slug,
                "status": "publish"
            }
        r = requests.get(url_srcdest, data=json.dumps(data), headers=headers, auth=(user, password))
        try:
            id = r.json()[0]['id']
        except:
            raise Exception(dict(slug=post_slug, request=r.json()))
    # Cambiar estado
    url_srcdest = 'https://activities.afinidata.com/wp-json/wp/v2/posts/%s' % (id)
    data = {
        'status': status
    }
    r = requests.post(url_srcdest, data=json.dumps(data), headers=headers, auth=(user, password))
    return True

def postlocale_change_status(language, status):
    ids = [680, 733, 734, 735, 736, 737, 738, 739, 740, 741, 742, 743, 744, 746, 747, 748, 749, 750, 757, 758, 766, 769,
           770, 771, 772, 773, 775,
           779, 780, 801, 802, 803, 804, 805, 806, 846, 847, 848, 849, 850,
           851, 852, 853, 854, 855, 856, 857, 858, 859, 860, 861, 1013, 1014, 1015, 1016, 1017, 1018, 1019, 1020, 1021,
           1022,
           1023, 1024, 1025, 1026, 1027, 1028, 1029, 1030, 1031, 1032, 1033, 1034, 1035, 1036, 1037, 1038, 1039, 1040,
           1041,
           1042, 1043, 1044, 1045, 1046, 1047, 1048, 1049, 1050, 1051, 1052, 1053, 1054, 1055, 1056, 1057, 1058, 1059,
           1060,
           1061, 1062, 963, 964, 965, 966, 968, 969, 970, 972, 973, 974, 975, 976, 979, 980, 981, 982, 983, 984, 985,
           986, 987, 988,
           989, 990, 991, 992, 993, 994, 995, 996, 997, 998, 999, 1000, 1002, 1003, 1004, 1006, 1007, 1008, 1009, 1010,
           1011, 1103,
           1105, 1106, 1107, 1108, 1109, 1112, 1114, 1116, 1117, 1118, 1119,
           1120, 1121, 1122, 1123, 1124, 1125, 1126, 1127, 1151, 1152, 1154, 1156, 1158, 1160, 1161, 1162, 1163, 1164,
           1165, 1166,
           1167, 1168, 1171, 1172, 1173, 1174, 1175, 913, 914, 915, 916, 917, 918, 919, 920, 921, 922, 923, 924, 925,
           926, 927, 928, 929,
           930, 931, 932, 933, 934, 935, 936, 937, 938, 939, 940, 941, 942, 943, 944, 945, 946, 947, 948, 949, 950, 951,
           952, 953, 954, 955, 956,
           957, 958, 959, 960, 961, 962]
    posts_locales = PostLocale.objects.filter(lang=language).filter(id__in=ids)
    for post_locale in posts_locales:
        post_name = post_locale.link_post \
            .replace('https://activities.afinidata.com/', '') \
            .replace('/', '')
        # Change status with the wordpress API
        if change_status_wordpress(post_name, status):
            print("ID:", post_locale.id, "Title:", post_locale.title)
        else:
            raise Exception(dict(slug=post_name))
    print("Total:",len(posts_locales))


postlocale_change_status('en', 'publish')
