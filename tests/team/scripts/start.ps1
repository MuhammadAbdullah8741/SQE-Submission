$ErrorActionPreference='Stop'
Set-Location (Resolve-Path "$PSScriptRoot/../../..")
$env:SPRING_DATASOURCE_URL='jdbc:mysql://localhost:3308/bookflow_test?useSSL=false&connectionTimeZone=%2B05:00&forceConnectionTimeZoneToSession=true&allowPublicKeyRetrieval=true'
$env:SPRING_DATASOURCE_USERNAME='root'
$env:SPRING_DATASOURCE_PASSWORD='SqeLocal2026'
$env:JAVA_TOOL_OPTIONS='-Duser.timezone=Asia/Karachi'
$env:BOOKFLOW_MAIL_SIMULATE='true'
$env:SERVER_PORT='8081'
$env:SERVER_ADDRESS='0.0.0.0'
java -jar target/bookflow.war
