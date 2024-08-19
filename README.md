<div align="center">

<!-- Title -->

<img src="media/auto-candidate.svg" alt="logo" width="200" height="auto" />
<h1>Auto Candidate</h1>

<!-- Badges -->

<p>
    <a href="">
        <img src="https://img.shields.io/github/last-commit/bivtor/auto-candidate" alt="last update" />
    </a>
    <a href="https://github.com/bivtor/auto-candidate/stargazers">
        <img src="https://img.shields.io/github/stars/bivtor/auto-candidate" alt="stars" />
    </a>
</p>
</div>

<br />

<!-- Table of Contents -->

# Table of Contents

- [About the Project](#about-the-project)
  - [Summary](#summary)
  - [Tech Stack](#tech-stack)
  - [Control Flow](#control-flow)
- [Contact](#contact)
- [Acknowledgements](#acknowledgements)

<!-- About the Project -->

# About the Project

<!-- Summary -->

### Summary

Auto Candidate is a tool I developed for Solution Based Therapeutics (SBT) to automate the process of aggregating data from various job boards and uploading it to a central database. It also interfaces with Twilio to send batch texts and emails.

What started as a project to assist with my role at SBT quickly grew into the complete solution. As its functionality expanded, so did its complexity, particularly to support parallelization, ultimately evolving into the robust tool it is today.

<!-- Tech Stack -->

### Tech Stack

<!-- Shields.io Badges: https://github.com/Ileriayo/markdown-badges -->

<details>
    <summary>Client</summary>
    <br />
    <a href="https://www.typescriptlang.org/">
        <img src="https://img.shields.io/badge/typescript-%23007ACC.svg?style=for-the-badge&logo=typescript&logoColor=white" alt="TypeScript" />
    </a>
    <a href="https://nextjs.org/">
        <img src="https://img.shields.io/badge/Next-black?style=for-the-badge&logo=next.js&logoColor=white" alt="NextJS" />
    </a>
    <a href="https://reactjs.org/">
        <img src="https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB" alt="ReactJS" />
    </a>
    <a href="https://sass-lang.com/">
        <img src="https://img.shields.io/badge/SASS-hotpink.svg?style=for-the-badge&logo=SASS&logoColor=white" alt="SASS" />
    </a>
</details>
<details>
    <summary>Server</summary>
    <br />
    <a href="https://fastapi.tiangolo.com/">
        <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" alt="FastAPI" />
    </a>
    <a href="https://docs.celeryq.dev/en/stable/index.html#">
        <img src="https://img.shields.io/badge/Celery-37814A?style=for-the-badge&logo=celery" alt="Celery" />
    </a>
    <a href="https://www.rabbitmq.com/">
        <img src="https://img.shields.io/badge/-rabbitmq-%23FF6600?style=for-the-badge&logo=rabbitmq&logoColor=white" alt="RabbitMQ" />
    </a>
    <a href="https://ngrok.com/">
        <img src="https://img.shields.io/badge/Ngrok-1F1E37?style=for-the-badge&logo=ngrok" alt="ngrok" />
    </a>
    <a href="https://www.python.org/">
        <img src="https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54" alt="Python" />
    </a>
    <a href="https://www.python.org/">
        <img src="https://img.shields.io/badge/Tampermonkey-00485B?style=for-the-badge&logo=tampermonkey" alt="Python" />
    </a>
    <a href="https://www.twilio.com/en-us">
        <img src="https://img.shields.io/static/v1?label=&message=Twilio&color=F22F46&labelColor=0D122B&logo=twilio&style=for-the-badge" alt="FastAPI" />
    </a>
    
</details>
<details>
    <summary>Database</summary>
    <br />
    <a href="https://sass-lang.com/">
        <img src="https://img.shields.io/badge/GraphQL-E10098?style=for-the-badge&logo=graphql" alt="SASS" />
    </a>
</details>
    
<details>
    <summary>Deployment</summary>
    <br />
    <a href="https://www.vercel.com/">
        <img src="https://img.shields.io/badge/-vercel-black?logo=vercel&logoColor=white&style=for-the-badge" alt="Vercel" />
    </a>
</details>

<!-- Control Flow -->

### Control Flow

Given the sensitive nature of some of the data involved in this project, I decided to use UserScripts for data extraction on locally hosted servers. These scripts then forward the extracted data to its final destination.

To manage the project's workflow more effectively, a Task Queue and Worker were implemented. While this introduced additional complexity and overhead, it also enabled parallelization of certain tasks, improving efficiency.

This project primarily handles two types of tasks: sending emails and messages, and aggregating and uploading data. The messaging aspect is relatively straightforward, but the candidate-adding process requires a more intricate control flow, which is detailed in the accompanying sequence diagram.

<a href='//www.plantuml.com/plantuml/png/dPCnRy8m48Lt_ueJ2-tGeOmPAYZgK8cMIY0n7yariGXsT6UW_VUrOu8SKQZeTl7xxjtpMHcBGtQxRQqKviuoh6ZzQXpn9-QaLED5dUi6ZOF1pEPOmxHYkwK1e1pB9QwX3vgIxQObtaFrcyk2U4_SCh7iGy--xIWlKJPlQB3qJ1zQMUwWM2gLfeU7fpW_yoDC0SuRgVOWA75g1Xye4gLuqjTOw98u4T6b0N7e4y4UMUEw9ad897a6KoPq1CDvGmPcsco6qLWbL6YADycWvLn5uK6Wr7l_TV1LxJjLP09zUe4kREDzrEcqTvdvOWbCigkTgBzIJee2SZI5Bi9ds3eyni1mL-coWeQrPUs-x__XDEgSQdj8Z2vi8ZxUbKGtzuswrKSoxNdvedntVG5oje6RRBhfSdRziSyRViGV'> 
    <img src="media/auto_candidate_flow.png" alt="Sequence Diagram"  height="auto" />
</a>

<!-- Contact -->

## Contact

#### Victor Rinaldi:

<a href="https://www.linkedin.com/in/victor-rinaldi-b1052a164">
    <img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn" />
</a>
<a href="https://www.vrinaldi.com/">
    <img src="https://img.shields.io/badge/-personal%20site-darkgrey?logo=code-review&logoColor=white&style=for-the-badge" alt="Personal Site" />
</a>

<!-- Acknowledgments -->

## Acknowledgements

- [Charles Zhang README](https://github.com/czhangy)
- [Shields.io](https://shields.io/)
- [PlantUML](https://plantuml.com/)
