# Smartnode

## Structure

* Paicoin node
* Counterparty node (API server and client)
* Worker
* Database (postgres)


**Scheme (draft)**

![alt text](images/smartnode-structure-v.0.0.1.png)

## ICO step by step guide 

*(preliminary)*

**1. Register ICO**

Initial Registration of ICO, intended for creating initial ICO config, register required parameters and  saving address of ICO owner
That method returns PAI address on which ICO assets will be created, so to issue new asset on that address we nned to have at least (??) 10 PAI coins

**2. Send PAI**

Send PAI coins on just created address. 

**3. Issue asset**

Create new asset which will be stored on above address

So after that 3 steps are finished we can start receive payments from differend PAI wallets to new created address nad send assets back to contributor.
In ICO initial config parameter "auto_payments" is True by default, so if required amount of PAI is on ICO address, assets will be sent to contributor in auto mode. If that parameter is False need to use workers methods:

*get_unpaid_transactions*

*pay_unpaid_transactions*

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
        "return_address": "pai_address",
        "quantity": 10000000,
        "asset": "asset_name",
        "quantity": 10000000000,
        "price": 1,
        "start_date": "2018-08-31 12:00:00",
        "end_date": "2018-08-31 12:00:00",
        "hard_cap": 1000000000,
        "soft_cap": 100000000000,
        "details": {
            "description": "Some TRUE description"
         }
      }
    }
}
</pre>
<b>Parameters:</b>
<table>
    <thead>
    <tr>
        <th>Parameter</th>
        <th>Description</th>
    </tr>
    </thead>
    <tbody>
    <tr>
        <td>return_address</td>
        <td>address where income PAIcoins will be transfers</td>
    </tr>
    <tr>
        <td>quantity</td>
        <td>*preliminary number of required tokens</td>
    </tr>
    <tr>
        <td>asset</td>
        <td>short asset name (BTC,XCP,PAI - not allowed)</td>
    </tr>
    <tr>
        <td>price</td>
        <td>desired token price token/pai</td>
    </tr>
    <tr>
        <td>start_date</td>
        <td>**ICO start date</td>
    </tr>
    <tr>
        <td>end_date</td>
        <td>**ICO end date</td>
    </tr>
    <tr>
        <td>hard_cap</td>
        <td>ICO hard cap</td>
    </tr>
    <tr>
        <td>soft_cap</td>
        <td>ICO soft cap</td>
    </tr>
    <tr>
        <td>details</td>
        <td>Optional parameter, saves any additional ICO info</td>
    </tr>
    </tbody>
</table>

<i>*that can be changed during asset issuance</i><br>
<i>**transactions before start and after end dates are not accepted and not saved</i>

<p><strong>Output</strong></p>
<pre>
{
  "SmartWorker": {
    "status": {
      "status": "SUCCESS",
      "progress": 100,
      "message": "Finished worker"
    },
    "output": {
      "response": {
          "source_address": "source_address"
      }
    },
    "worker_data": {
      "workerIpAddress": "172.31.27.70",
      "workerEnvironment": "Environment"
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
<p><strong>Output</strong></p>
<pre>
{
  "SmartWorker": {
    "status": {
      "status": "SUCCESS",
      "progress": 100,
      "message": "Finished worker"
    },
    "output": {
      "response": {
          "ico_info": "ico_info_json"
      }
    },
    "worker_data": {
      "workerIpAddress": "172.31.27.70",
      "workerEnvironment": "Environment"
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
    }
}
</pre>
<p><strong>Output</strong></p>
<pre>
{
  "SmartWorker": {
    "status": {
      "status": "SUCCESS",
      "progress": 100,
      "message": "Finished worker"
    },
    "output": {
      "response": {
          "ico_list": ["ico_list"]
      }
    },
    "worker_data": {
      "workerIpAddress": "172.31.27.70",
      "workerEnvironment": "Environment"
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
        "description": "description of new asset",
        "fee": 10000
      }
    }
}
</pre>
<table>
    <thead>
    <tr>
        <th>Parameter</th>
        <th>Description</th>
    </tr>
    </thead>
    <tbody>
    <tr>
        <td>asset</td>
        <td>short asset name (BTC,XCP,PAI - not allowed)</td>
    </tr>
    <tr>
        <td>quantity</td>
        <td>*preliminary number of required tokens</td>
    </tr>
    <tr>
        <td>source</td>
        <td>*pai address</td>
    </tr>
    <tr>
        <td>description</td>
        <td>short description of asset</td>
    </tr>
    <tr>
        <td>fee</td>
        <td>fee for PAI miners</td>
    </tr>
    </tbody>
</table>

<i>*address generated by smart node and got in register_ico method</i>

<p><strong>Output</strong></p>
<pre>
{
  "SmartWorker": {
    "status": {
      "status": "SUCCESS",
      "progress": 100,
      "message": "Finished worker"
    },
    "output": {
      "response": {
          "signed_tx_hex": "signed_hex"
      }
    },
    "worker_data": {
      "workerIpAddress": "172.31.27.70",
      "workerEnvironment": "Environment"
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
        "ico": "ico_name",
        "params": [params]
      }
    }
}
</pre>
<p><strong>Output</strong></p>
<pre>
{
  "SmartWorker": {
    "status": {
      "status": "SUCCESS",
      "progress": 100,
      "message": "Finished worker"
    },
    "output": {
      "response": {
          "unpaid_transactions": ["transactions_list"]
      }
    },
    "worker_data": {
      "workerIpAddress": "172.31.27.70",
      "workerEnvironment": "Environment"
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
<p><strong>Output</strong></p>
<pre>
{
  "SmartWorker": {
    "status": {
      "status": "SUCCESS",
      "progress": 100,
      "message": "Finished worker"
    },
    "output": {
      "response": {
          "paid_transactions": ["paid_transactiosn_list_with_txids"]
      }
    },
    "worker_data": {
      "workerIpAddress": "172.31.27.70",
      "workerEnvironment": "Environment"
    }
  }
}
</pre>
</details>