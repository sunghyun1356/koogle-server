import datetime

def to_time(time_str): 
        try: 
            return datetime.time(*map(int, time_str.split(':')))
        except Exception as e:
            return None
        
def to_day_of_week_eng(day_str):
    kor_eng = {
        '월': 'Mon', 
        '화': 'Tue', 
        '수': 'Wed', 
        '목': 'Thu', 
        '금': 'Fri', 
        '토': 'Sat', 
        '일': 'Sun'
    }
    day_str = next((k for k in kor_eng if (k in day_str)), None) # "화(8\u002F15)" -> "화"
    return kor_eng.get(day_str, None)

class NestedDictConverter:
    @staticmethod
    def _get_value_from_nested_dict(nested_dict, keys):
            ret = nested_dict
            for key in keys:
                try: 
                    ret = ret[key]
                except (KeyError, IndexError, TypeError):
                    return None
            return ret

    @staticmethod
    def convert_obj_by_rules(obj, rules):
        res = {}

        for key, rule in rules.items():
            val = NestedDictConverter._get_value_from_nested_dict(obj, rule['lookup'])
            if 'post_apply' in rule:
                for func in rule['post_apply']:
                    val = func(val)
            res[key] = val

        return res

    @staticmethod
    def convert_list_by_rules(list, rules):
        res = []

        for obj in list:
            converted_obj = NestedDictConverter.convert_obj_by_rules(obj, rules)
            res.append(converted_obj)

        return res