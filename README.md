# iac-aws-cdk 
aws-cdk python 프로젝트

## Table of Contents
- [Introduction](#Introduction)
- [Technologies Used](#Technologies-Used)
- [Setup](#Setup)
- [Usage](#Usage)
- [Acknowledgements](#Acknowledgements)

## Introduction
- aws-cdk를 사용해 AWS 리소스 배포

## Technologies Used
- Python: 3.9

## Setup
- `config/prod.ini.default`
    - stack별로 설정값 입력 후 `config/prod.ini`로 파일명 변경 
- 환경 구성 
    ```shell
    $ brew install awscli
    $ npm install -g aws-cdk

    $ pipenv shell --python 3.9
    $ python -V
    $ pipenv install
    ```

## Usage
- 신규 stack은 `iac_aws_cdk`디렉토리 하위에 생성
    - `app.py`에 추가한 stack 정보 추가
- 리소스 정보 출처
    - https://docs.aws.amazon.com/cdk/api/v1/python/index.html
- <stack명>: `app.py`에 명시된 stack
- <프로필명>: `~/.aws/credentials`에 명시된 프로필명
- <리전명>: 배포하려는 stack의 리전 (eg. `ap-northeast-2`)

- boostrap
    ```shell
    $ account_id=$(aws sts get-caller-identity --profile <프로필명> --query Account --output text)
    $ cdk boostrap aws://$account_id/<리전명> --profile <프로필명>
    ```
- preview stack
    ```shell
    $ cdk synth <stack명> --profile <프로필명>  # cloudformation형태로 출력
    $ cdk diff <stack명> --profile <프로필명>  # stack 업데이트하는 경우
    ```
- deploy stack
    ```shell
    $ cdk deploy <stack명> --profile <프로필명>
    ```
- destroy stack 
    ```shell
    $ cdk destroy <stack명> --profile <프로필명>
    ```
