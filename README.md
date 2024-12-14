# IMDb Movies Recommender System
**Introduction to Data Science Capstone Project - Group 08**
---
## Overview
Movie is a popular form of entertainment and with countless options available of options available on platforms like IMDb, helping users discover films that match their taste has become increasingly valuable. This project focuses on developing a personalized movie recommender system using the movies dataset collected from the IMDb platform.

## Project Organization

```
checkpoint/                 # model deployment
data/                       # raw data
demo/                       # demo application
docs/                       # project report and presentation
notebooks/                  # main notebooks
scraper/                    # scraper folder
.gitignore
README.md 
requirements.txt            # requirement libraries
```

## Setup
Change the working directory to the project root, change the path of the project properly and then install required packages and libraries.
```bash
    pip install -r requirements.txt
```

Application demo using command for both client and server side:

```bash
    # client
    cd DsProject_Imdb/demo/client
    npm i
    npm start
```

```bash
    # server
    cd DsProject_Imdb/demo/server
    python -m app
```
The website can be accessed at
* Client: http://localhost:3000
* Server: http://localhost:5000

## Collaborators
<table>
    <tbody>
        <tr>
            <th align="center">Member name</th>
            <th align="center">Student ID</th>
        </tr>
        <tr>
            <td>Nguyễn Chí Long</td>
            <td align="center"> 20210553&nbsp;&nbsp;&nbsp;</td>
        </tr>
        <tr>
            <td>Ngô Xuân Bách</td>
            <td align="center"> 20215181&nbsp;&nbsp;&nbsp;</td>
        </tr>
        <tr>
            <td>Lê Xuân Hiếu</td>
            <td align="center"> 20215201&nbsp;&nbsp;&nbsp;</td>
        </tr>
        <tr>
            <td>Đinh Việt Quang</td>
            <td align="center"> 20215235&nbsp;&nbsp;&nbsp;</td>
        </tr>
        <tr>
            <td>Nguyễn Viết Thuận</td>
            <td align="center"> 20210826&nbsp;&nbsp;&nbsp;</td>
        </tr>
    </tbody>
</table>