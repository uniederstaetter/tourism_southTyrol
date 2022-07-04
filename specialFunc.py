from datetime import date, datetime

def translateTagList(tags):
    numberedList = []
    for tag in tags:
        if tag == 'water':
            numberedList.append(1)
        elif tag == 'flora':
            numberedList.append(2)
        elif tag == 'fauna':
            numberedList.append(3)
        elif tag == 'protected natural heritage':
            numberedList.append(4)
        elif tag == 'protected cultural heritage':
            numberedList.append(5)
        elif tag == 'events':
            numberedList.append(6)
        elif tag == 'cultural and religious institutions':
            numberedList.append(7)
        elif tag == 'health resorts':
            numberedList.append(8)
        elif tag == 'sport and recreation facilities':
            numberedList.append(9)
        elif tag == 'tourism paths, trails and roads':
            numberedList.append(10)
        elif tag == 'indoor':
            numberedList.append(11)
        elif tag == 'outdoor':
            numberedList.append(12)
        elif tag == 'food&shopping':
            numberedList.append(13)
    return numberedList


def addSeasonTraj(row, seasons, Y):
    date = datetime.strptime(row['date'], '%d.%m.%Y %H:%M')
    date = date.date()
    date = date.replace(year=Y)
    return next(season for season, (start, end) in seasons
                if start <= date <= end)


def applySeasons(trajectories):
    """
    :return: the trajectories with an additional season attribute e.g (Winter, Spring, etc.)
    """
    trajectories_toModify = trajectories
    Y = 2000  # dummy leap year to allow input X-02-29 (leap day)
    seasons = [('Winter', (date(Y, 1, 1), date(Y, 3, 20))),
               ('Spring', (date(Y, 3, 21), date(Y, 6, 20))),
               ('Summer', (date(Y, 6, 21), date(Y, 9, 22))),
               ('Autumn', (date(Y, 9, 23), date(Y, 12, 20))),
               ('Winter', (date(Y, 12, 21), date(Y, 12, 31)))]
    trajectories_toModify['season'] = trajectories_toModify.apply(lambda row: addSeasonTraj(row, seasons, Y), axis=1)
    return trajectories_toModify
