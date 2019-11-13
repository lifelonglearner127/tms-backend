# tms-backend
Vehicle Management System
- [Introduction](#introduction)
- [Important Notes](#important-notes)
- [More docs](doc/README.md)
    - [About Project](doc/project.md)
    - [Workflow](doc/workflow.md)
    - [Development](doc/development.md)
    - [Deployment](doc/deployment.md)
    - [DB](doc/backup.md)
- [G7 Sample Request & Response](tms/g7/ReadMe.md)
> You need to take a look this document step by step before getting started.

### Introduction
> This system is based on micro-service architecture and this code repository contains backend. You can find the front end code at [here](https://github.com/lifelonglearner127/tms-frontend)

This system manages the trucks equipped with [G7](https://www.g7.com.cn/) device. G7 devices upload the various sensor data based on MQTT protocol to G7 Cloud server. We can get uploaded data from G7 Cloud Server using REST API and Push. You can see all functionalities G7 provided at [here](http://openapi.huoyunren.com/app/docopenapi/#/index)

This system consist of following functionalities.
 - Monitoring(实时监控)
 - Order(订单管理)
 - Routing(行程管理)
 - Workdiary(工作单)
 - Report(系统报表)
 - Financial management(财务管理)
 - Vehicle Management(车辆管理)
 - Business workflow(业务处理)
 - Security(安全管理)
 - Company Policy(公司制度管理)
 - Warehouse(仓库管理)
 - Basic Setting(基础数据)
 - Company Management(公司管理)
> This is based on customer requirements so my backend project do not rely on this structure

### Important Notes
 - Monitoring
    - G7 positioning data is based on WGS84(international coordinates) so please confirm your map coordination system with G7 coordinates.
    - Take a look at following urls
        - [G7 Positioning Data](http://openapi.huoyunren.com/app/docopenapi/#/productCenter/pushApi/detail?code=location&mqttPush=1&httpPush=1&desc=%E8%AE%BE%E5%A4%87%E4%B8%8A%E4%BC%A0%E7%9A%84%E8%BD%A6%E8%BE%86GPS%E5%AE%9A%E4%BD%8D%E6%95%B0%E6%8D%AE%28%E7%BB%8F%E7%BA%AC%E5%BA%A6%E6%95%B0%E6%8D%AE%29,%E6%95%B0%E6%8D%AE%E9%87%8F%E6%AF%94%E8%BE%83%E5%A4%A7)
        - [Gaode Map Coordination Coverision](https://lbs.amap.com/api/javascript-api/guide/transform/convertfrom)
 - Order
 - Routing
 - Workdiary