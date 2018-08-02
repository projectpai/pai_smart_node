# Smartnode

## Structure

* Paicoin node
* Counterparty node (API server and client)
* Worker
* Database (postgres)


**Scheme (draft)**

![alt text](images/smartnode-structure-v.0.0.1.png)

## Worker

Uses DevSmartNodeSQS queue

**Methods (to be updated)**

<details>
<summary><strong>Register ICO</strong></summary>
<br>
<p>Saves primary ICO inforamtion</p>
<p><strong>Example SQS message</strong></p>
<pre>
{
    "redisData": {
      "redisChannel": "id"
    },
    "input": {
      "method": "register_ico",
      "params": {
        "ico_name": "My coolest ICO",
        "start_date": "start_date",
        "end_date": "end_date",
        "asset": "BTC",
        "quantity": 10000000,
        "divisible": "True",
        "description": "description of new asset",
        "fee": 10000
      }
    }
}
</pre>
</details>

<details>
<summary><strong>Get ICO info</strong></summary>
<br>
<p>Get information about ICO</p>
<p><strong>Example SQS message</strong></p>
<pre>
{
    "redisData": {
      "redisChannel": "id"
    },
    "input": {
      "method": "get_ico_info",
      "params": {
        "source": "pai_address_associated_with_ico"
      }
    }
}
</pre>
</details>

<details>
<summary><strong>List of all ICO</strong></summary>
<br>
<p>Get information about all ICO</p>
<p><strong>Example SQS message</strong></p>
<pre>
{
    "redisData": {
      "redisChannel": "id"
    },
    "input": {
      "method": "list_ico",
      "params": {
        (?)
      }
    }
}
</pre>
</details>

<details>
<summary><strong>Issue new asset</strong></summary>
<br>
<p>Create new asset</p>
<p><strong>Example SQS message</strong></p>
<pre>
{
    "redisData": {
      "redisChannel": "id"
    },
    "input": {
      "method": "issuance",
      "params": {
        "source": "address",
        "quantity": 10000000,
        "asset": "BTC",
        "divisible": "True",
        "description": "description of new asset",
        "fee": 10000
      }
    }
}
</pre>
</details>

<details>
<summary><strong>Get unpaid transactions</strong></summary>
<br>
<p>Returns list of all unpaid transactions</p>
<p><strong>Example SQS message</strong></p>
<pre>
{
    "redisData": {
      "redisChannel": "id"
    },
    "input": {
      "method": "get_unpaid_transactions",
      "params": {
        (?)
      }
    }
}
</pre>
</details>

<details>
<summary><strong>Pay unpaid transactions</strong></summary>
<br>
<p>Send required amount of asset to contributor</p>
<p><strong>Example SQS message</strong></p>
<pre>
{
    "redisData": {
      "redisChannel": "id"
    },
    "input": {
      "method": "pay_unpaid_transactions",
      "params": {
        [transactions_list]
      }
    }
}
</pre>
</details>