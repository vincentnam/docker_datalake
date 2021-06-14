import datetime


# Transform a date to standard format
def format_date(date, cus_format = None):
    """
    :param date: str : date to format
    :param cus_format: str : custom format : see strptime doc for
    format formatting.
    :return: str : formated date
    """
    # Transform a string date into a standard format by trying each
    # date format. If you want to add a format, add a try/except in the
    # last except
    # date : str : the date to transform
    # return : m : timedata : format is YYYY-MM-DD HH:MM:SS
    if format is not None :
        date_str = date
        #
        date_str = date_str.replace("st","").replace("th","")\
            .replace("nd","").replace("rd","").replace(" Augu "," Aug ")
        format_list = ["%d %B %Y","%d %b %Y","%Y/%m/%d","%d/%m/%Y %H:%M:%S","%Y-%m-%d %H:%M:%S","%d %m %Y", "%d %m %Y","%Y-%m-%d"]

        for date_format in format_list:
            try:
                return datetime.datetime.strptime(date_str, date_format)
            except ValueError:
                pass
        raise ValueError("Format not recognised. \nConsider "
                                          "adding a date format "
                                          "in the function \"format_date\".")
    else :
        try :
            return datetime.datetime.strptime(date, cus_format)
        except ValueError as e:
            print("Format not recognised. \nConsider "
                                          "adding a date format "
                                          "in the function \"format_date\".")
            raise e
