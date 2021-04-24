''' In this project we are scrapping git hun titles page'''

# get the title page 
import os
import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_topics_page():
    #this function will return a doc that has all the html parsered inside it.
    topics_url = 'https://github.com/topics'
    response = requests.get(topics_url)
    if response.status_code != 200:
        raise Exception('Failed to load page {}'.format(topics_url))
    doc = BeautifulSoup(response.text, 'html.parser')
    return doc 

# now get the title of each topic on the page and put then in a list called topic_titles.

def get_topic_titles(doc):
    selection_class = 'f3 lh-condensed mb-0 mt-1 Link--primary'
    topic_title_tags = doc.find_all('p', {'class': selection_class})
    topic_titles = []
    for tag in topic_title_tags:
        topic_titles.append(tag.text)
    return topic_titles    
# similarly get the topic description and put that in a list called as topic_descs.
def get_topic_descs(doc):
    desc_selector = 'f5 color-text-secondary mb-0 mt-1'
    topic_desc_tags = doc.find_all('p', {'class': desc_selector})
    topic_descs = []
    for tag in topic_desc_tags:
        topic_descs.append(tag.text.strip())
    return topic_descs

#get the url of each topic and add them to topic_urls list.
 
def get_topic_urls(doc):
    topic_link_tags = doc.find_all('a', {'class': 'd-flex no-underline'})
    topic_urls = []
    base_url = 'https://github.com'
    for tag in topic_link_tags:
        topic_urls.append(base_url + tag['href'])
    return topic_urls    

#put them all together in a dictionary and return the dataframe
def scrape_topics():
    topics_url = 'https://github.com/topics'
    response = requests.get(topics_url)
    if response.status_code != 200:
        raise Exception('Failed to load page {}'.format(topics_url))
    doc = BeautifulSoup(response.text, 'html.parser')
    topics_dict = {
        'title': get_topic_titles(doc),
        'description': get_topic_descs(doc),
        'url': get_topic_urls(doc)
    }
    return pd.DataFrame(topics_dict) 


docs = get_topics_page()
titles =get_topic_titles(docs)
desc = get_topic_descs(docs)
url = get_topic_urls(docs)
dataframe = scrape_topics() 

# Now write this infomation to csv file

dataframe.to_csv('title_page_info.csv',index=None)


'''                   get the top 25 repos from title page                   '''



def get_topic_page(topic_url):
    response = requests.get(topic_url)
    content = response.text
    with open('titlepage.html','w') as f:
        f.write(content)
    doc2 = BeautifulSoup(content,'html.parser')
    return doc2

def convert_star_to_int(star_str):
    if star_str[-1] == 'k':
        return int(float(star_str[ : -1])*1000)
    else:
        return int(star_str)



def get_repo_info(repo_tags,star_tag):
    base_url = "https:/github.com"
    a_tags = repo_tags.find_all('a')
    username = a_tags[0].text.strip()
    repo_name = a_tags[1].text.strip()
    repo_url = base_url + a_tags[1]['href']
    stars = convert_star_to_int(star_tag.text.strip())
    return username, repo_name,repo_url,stars 

def get_topic_repos(doc2):
    repo_tags = doc2.find_all('h1',{'class' : 'f3 color-text-secondary text-normal lh-condensed'})
    star_tag = doc2.find_all('a',{'class':'social-count float-none'})
    final_dic = {
    'username':[],
    'stars': [],
    'repo_name':[],
    'repo_url':[]
    } 


    for i in range(len(repo_tags)):
        repo_info = get_repo_info(repo_tags[i],star_tag[i])
        final_dic['username'].append(repo_info[0])
        final_dic['repo_name'].append(repo_info[1])
        final_dic['repo_url'].append(repo_info[2])
        final_dic['stars'].append(repo_info[3])

    final_dic_df = pd.DataFrame(final_dic)
    return final_dic_df

def scrape_topic(topic_url, path):
    if os.path.exists(path):
        print("The file {} already exists. Skipping...".format(path))
        return
    topic_df = get_topic_repos(get_topic_page(topic_url))
    topic_df.to_csv(path, index=None)


def scrape_topics_repos():
    print('Scraping list of topics')
    topics_df = scrape_topics()
    
    for index,row in topics_df.iterrows():
        print('Scraping top repositories for "{}"'.format(row['title']))
        scrape_topic(row['url'], row['title'])

scrape_topics_repos()









