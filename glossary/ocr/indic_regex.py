
# The regex codes for various languages

def regex(lang):
    unicodes = {
        "en" : r'[\u0041-\u005a\u0061-\u007a]+',
        "hi" : r'[\u0900-\u097F]+',
        "as" : r'[\u0980-\u09FF]+',
        "brx" : r'[\u0900-\u097F]+',
        "bd" : r'[\u0900-\u097F]+',
        "bn" : r'[\u0980-\u09FF]+',
        "gom" : r'[\u0900-\u097F]+',
        "gu" : r'[\u0A80-\u0AFF]+',
        "kha" : r'[\u0980-\u09FF]+',
        "kn" : r'[\u0C80-\u0CFF]+',
        "ks" : r'[\u0600-\u06FF]+',
        "mai" : r'[\u0020-\u0040\u005B-\u0060\u007B-\u007E\u00A0\u00A7\u00A9\u0902-\u0903\u0905-\u090C\u090F-\u0910\u0913-\u0918\u091A-\u0928\u092A-\u0930\u0932\u0935-\u0939\u093C\u093E-\u0942\u0947-\u0948\u094B-\u094D\u0961\u2011\u2013-\u2014\u2018-\u2019\u201C-\u201D\u2026\u2030\u2032-\u2033\u20AC]+',
         "ml" : r'[\u0D00-\u0DFF]+',
         "mni" : r'[\uABC0-\uABFF]+',
         "mr" : r'[\u0900-\u097F]+',
         "ne" : r'[\u0900-\u097F]+',
         "or" : r'[\u0B00-\u0B7F]+',
         "pa" : r'[\u0A00-\u0A7F]+',
         "sa" : r'[\u0900-\u097F]+',
         "sat" : r'[\u1C50-\u1C7F]+',
         "sd" : r'[\u0660-\u0669\u06F0-\u06F9]+',
         "ta" : r'[\u0B80-\u0BFF]+',
         "te" : r'[\u0C00-\u0C7F]+',
         "ur" : r'[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]+'

    }
    return unicodes[lang]

