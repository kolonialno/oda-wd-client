# Oda Workday client
A Python client library made for Oda's implementation of the various Workday APIs.

Released publically for inspiration and ease of implementation on our end, but is not maintained based on community
needs.

# Usage
Import the relevant client services from `.api`, and type definitions from `.types.$SERVICE`. Importing business 
logic directly from inside `.service` should not be required.

Example:

```python
# Get all workers with currently active data
from datetime import date
from oda_wd_client.api import HumanResources

hr = HumanResources(
    base_url="https://wd3-impl-services1.workday.com/",
    tenant_name="mycompany",
    username="admin",
    password="hunter2"
)

all_workers = list(hr.get_workers(as_of_date=date.today()))

# If the result is not cast to a list, you get a generator that can be iterated over and will only get new data (new 
# page in paginated data) when required

```


## Structure
All API services are exposed under `oda_wd_client.api`. Each WWS service has a separate directory structure under 
`oda_wd_client.service`, where specific logic for each service is collected. The common definitions and bases are 
collected under `oda_wd_client.base`.

The import hierarchy is as following,

* `.api` imports from `.service.$SERVICE.api`, which import from `.base.api`
* `.service.$SERVICE.api` imports from `. service.$SERVICE.types` and `.service.$SERVICE.utils`
* `.service.$SERVICE.utils` imports from `.base.utils` and `.service.$SERVICE.types`
* `.service.$SERVICE.types` imports from `.base.types`
* `.base.tools` should not import anything from this package, so importing from `.base.tools` should be safe anywhere
