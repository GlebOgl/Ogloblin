import pandas as pd
from multiprocessing import Queue, Process
from pathlib import Path
import math


def get_salary(x, currencies):
    salary_from = x.loc['salary_from']
    salary_to = x.loc['salary_to']
    salary_currency = x.loc['salary_currency']
    published_at = x.loc['published_at']
    currencies_to_work = list(currencies.loc[:, ~currencies.columns.isin(['date'])].columns.values)
    date = published_at[:7]
    if math.isnan(salary_to) or math.isnan(salary_from):
        salary = salary_to if math.isnan(salary_from) else salary_from
    else:
        salary = math.floor((salary_from + salary_to) / 2)
    if salary_currency == 'RUR' or salary_currency not in currencies_to_work:
        return salary
    return math.floor(salary * currencies.loc[currencies['date'] == date][salary_currency].values[0])


def fill_df(df, currencies):
    df['salary'] = df.apply(lambda x: get_salary(x, currencies), axis=1)
    df.drop(columns=['salary_from', 'salary_to', 'salary_currency'], inplace=True)
    df = df.reindex(columns=['name', 'salary', 'area_name', 'published_at'], copy=True)
    return df


def read_csv_year(args, q):
    folder = args[0]
    name = args[1]
    prof = args[2]
    currencies = args[3]
    df = pd.read_csv(folder + '/' + name + '.csv')
    df = fill_df(df, currencies)
    data_job = df[df['name'].str.contains(prof, case=False)]
    q.put([int(df['published_at'].values[0][:4]), df.shape[0], math.floor(df['salary'].mean()), data_job.shape[0], math.floor(data_job['salary'].mean()), df])


if __name__ == '__main__':
    folder = input('Введите название папки с файлами: ')
    prof = input('Введите название профессии: ')
    salary_dynamic = {}
    count_dynamic = {}
    salary_prof_dynamic = {}
    prof_count = {}
    new_df = pd.DataFrame()
    path = Path(folder)
    dfs = []
    currencies = pd.read_csv('currencies.csv')
    years_count = len(list(path.iterdir()))
    years = []
    for i in range(0, years_count):
        years.append([folder, f"{2003 + i}", prof, currencies.copy()])
    q = Queue()
    x = []
    for year in years:
        p = Process(target=read_csv_year, args=(year, q))
        x.append(p)
        p.start()

    for i in range(0, years_count):
        p = x[i]
        p.join(1)
        data = q.get()
        year = data[0]
        salary_dynamic[year] = data[1]
        count_dynamic[year] = data[2]
        salary_prof_dynamic[year] = data[3]
        prof_count[year] = data[4]
        dfs.append(data[5])

    print('Динамика уровня зарплат по годам:', salary_dynamic)
    print('Динамика количества вакансий по годам:', count_dynamic)
    print('Динамика уровня зарплат по годам для выбранной профессии:', salary_prof_dynamic)
    print('Динамика количества вакансий по годам для выбранной профессии:', prof_count)

    new_df = pd.concat(dfs)

    new_df.to_csv('vac_with_sal.csv', index=False)
