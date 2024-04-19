# Lambda-Coinmarket
A python lambda function that uses the coinmarketcap API to get the price of ETH and Bitcoin and then inserts it into the database.

## Dependencies

- urllib3
- mysqlconnector

The function needs this libraries in order to work correclty

## Installation

```sh
pip install urllib3==1.26.6
```
Install this specific version for conflicts with lambda: 
ImportError: urllib3 v2.0 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with LibreSSL 2.8.3
This text you see here is *actually- written in Markdown! To get a feel
for Markdown's syntax, type some text into the left window and
watch the results in the right.

```sh
pip mysql-connector-python
```


## Lambda

To upload to lambda and work correctly is neccesary to attach the dependencies with the function. Lambda has a limit of 10mb per .zip uploaded, but with lambda layers we can upload dependencies and still edit our function from the lambda console.


