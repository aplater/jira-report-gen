# Jira CSV Report Generator

Python script to search Jira tickets using JQL. Returned tickets will match the search string and customer organization provided as command arguments. A generated XLSX of the records will be emailed using the SMTP values provided by runtime arguments.

As currently defined in [main.py](main.py), results will be from the EXAMPLE project and only include tickets created in the last 7 days.

## Getting Started
* Add Jira Cloud API key information and API url
* Update JQL Query

### Prerequisites
* Python 3.X+
  * [pandas](https://pandas.pydata.org/)
  * [Requests](https://2.python-requests.org/en/master/)
* SMTP server with anonymous relay enabled
* Jira Cloud instance
  * API key

## Deployment
main.py customer_jira_org_name search_string smtp_server_address smtp_port recipient email sender

## Authors
* **Lee Herlinger** - [herlincl](https://github.com/herlincl/)

## License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## References
* [Jira Cloud REST API V2](https://developer.atlassian.com/cloud/jira/platform/rest/v2/)
* [JQL Formatting](https://support.atlassian.com/jira-service-desk-cloud/docs/use-advanced-search-with-jira-query-language-jql/)
* [MaxResults is not part of API spec](https://confluence.atlassian.com/jirakb/changing-maxresults-parameter-for-jira-cloud-rest-api-779160706.html)
