# -*- coding: utf-8 -*-
import argparse
import datetime
import hashlib
import os
import pickle
import requests
import time

from prettytable import PrettyTable
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Problem:
    def __init__(self, link, topic='', level='', desc=''):
        self.link             = link
        self.topic            = topic
        self.level            = level
        self.decs             = desc
        self.picked_time      = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.picked_timestamp = time.time()

    def __lt__(self, other):
        return self.picked_timestamp < other.picked_timestamp

    def __str__(self):
        return '{} [{}][{}]'.format(self.link, self.topic, self.level)


def hash(url):
    return hashlib.md5(url.encode('utf-8')).hexdigest()


def jump_to_leetcode(url, jump=False, mac_os=False):
    if jump:
        if mac_os:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--kiosk')  # for Mac OS
            browser = webdriver.Chrome(options=chrome_options)
            browser.get(url)
        else:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('headless')  # for Linux
            browser = webdriver.Chrome(options=chrome_options)
            browser.get(url)
    else:
        print(url)


def pick_one():
    tries = 0
    while 1:
        resp = requests.get(
            url='https://leetcode.com/problems/random-one-question/all')
        if resp.status_code == 200:
            # TODO: store more useful information
            url = resp.url
            if not os.path.exists('picked.pickle'):
                with open('picked.pickle', 'wb') as writer:
                    pickle.dump({hash(url): Problem(url)}, writer)
            else:
                look_table = {}
                with open('picked.pickle', 'rb') as reader:
                    look_table = pickle.load(reader)
                if hash(url) in look_table:
                    continue
                else:
                    look_table[hash(url)] = Problem(url)
                    with open('picked.pickle', 'wb') as writer:
                        pickle.dump(look_table, writer)
                    jump_to_leetcode(url)
                    break
        else:
            print("failed to pick one, just try again")
            tries += 1
            if tries == 3:
                print("seem to fail to pick one from leetcode, please check your network")
                break
            time.sleep(2)


def print_all_picked_ones():
    table = PrettyTable()
    table.field_names = ['Picked Time', 'Link', 'Topic', 'Level']
    table.align["Link"] = "l"

    problems = []
    with open('picked.pickle', 'rb') as reader:
        db = pickle.load(reader)
        problems = [problem for problem in db.values()]

    problems.sort(reverse=True)

    for problem in problems:
        table.add_row([problem.picked_time, problem.link, problem.topic, problem.level])

    print(table)


def print_10_picked():
    table = PrettyTable()
    table.field_names = ['Picked Time', 'Link', 'Topic', 'Level']
    table.align["Link"] = "l"

    problems = []
    with open('picked.pickle', 'rb') as reader:
        db = pickle.load(reader)
        problems = [problem for problem in db.values()]

    problems.sort(reverse=True)

    for problem in problems[:10]:
        table.add_row([problem.picked_time, problem.link, problem.topic, problem.level])

    print(table)


def output_all_picked_ones_to_html():
    table = PrettyTable()
    table.field_names = ['Picked Time', 'Link', 'Topic', 'Level']
    table.align["Link"] = "l"

    problems = []
    with open('picked.pickle', 'rb') as reader:
        db = pickle.load(reader)
        problems = [problem for problem in db.values()]

    problems.sort(reverse=True)

    for problem in problems:
        table.add_row([problem.picked_time, problem.link, problem.topic, problem.level])

    # install "open in browser" in vscode to open current html file in default browser
    with open('picked_problems.html', 'w') as writer:
        writer.write(table.get_html_string())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--pick', help='pick one leetcode problem', action='store_true')
    parser.add_argument(
        '--print', help='print all picked problems', action='store_true')
    parser.add_argument(
        '--less_print', help='print latest 10 picked problems', action='store_true')
    parser.add_argument(
        '--html', help='show all picked problems in html format', action='store_true')
    
    args = parser.parse_args()
    if args.pick:
        pick_one()
    elif args.print:
        print_all_picked_ones()
    elif args.less_print:
        print_10_picked()
    elif args.html:
        output_all_picked_ones_to_html()
    else:
        print('unknown input')
