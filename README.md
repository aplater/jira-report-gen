# Jira CSV Report Generator

Python script to search Jira tickets using JQL. Returned tickets will match the search string and customer organization provided as command arguments. A generated CSV of the records will be emailed using the smtp values provided by arguments called at runtime.

As currently defined in [main.py](main.py), results will be from the EXAMPLE project and only include tickets created in the last 7 days.


## Getting Started

* Add Jira Cloud API key information and API url
* Update project key to match the desired search location

### Prerequisites

* Python 3.8+
* SMTP server with anonymous relay enabled


## Deployment

main.py customer_jira_org_name search_string smtp_server_address smtp_port recipient email sender


## Authors

* **Lee Herlinger** - [herlincl](https://github.com/herlincl/)

## License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
