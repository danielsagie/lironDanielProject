# *DevOps Project - App*

Our web application will revolutionize your shopping experience, offering a fresh and exciting approach.

This repository includes all the necessary files for deploying the web app, along with a CI workflow and pytest tests to ensure its quality.


## Repo Folders

<details>
  <summary><b>.github/workflows</b></summary>
  <details>
  <summary>CI.yaml</summary>
    Implement a container that test the web app with pytest. then it build docker image, push it to dockerhub and notify collaborator that image is updated. it also changes the image version inside the infrastracture repo.in case of failing on one of the stages it will notify that workflow failed. 
 
    

  </details>

    
 

 
</details>
<details>
  <summary><b>app</b></summary>
  
* image files saved in "static", web pages htmls saved in "template.
* dockerfile, docker-compose and requirements for containerization.
* python file that runs DB and flask
</details>

<details>
  <summary><b>modules</b></summary>
  
* contains database configuration with pymongo
</details>

<details>
  <summary><b>test</b></summary>
  
* contains the tests that pytest will run 
</details>

## *Screenshots*
<img width="917" alt="web1" src="https://github.com/danielsagie/project_app/assets/137056545/fe88298e-2bd5-4d06-8d24-e3743b1da061">
<img width="917" alt="web2" src="https://github.com/danielsagie/project_app/assets/137056545/099a1df2-b973-49a4-901a-0ee393778d0e">





## *Project Repos*
- [infrastructure](https://github.com/danielsagie/project_conf)
- [Web-App](https://github.com/danielsagie/project_app)





<img width="658" alt="Capture" src="https://github.com/danielsagie/project_conf/assets/137056545/fd66a481-c4df-44fc-a2ab-23ec9633a50d">
