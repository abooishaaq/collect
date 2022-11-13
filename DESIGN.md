# Two Approaches

## Approach 1

Make a call to webhooks after a form submission with all the data in the form.

## Approach 2

Make a call to webhooks after a form submission with a form id with the result of a query.
Different webhooks can validate different parts of a huge form submission. Also, I'll allow to maek queries for fields of a form_id.

**I find Approach 2 to be more flexible and scalable.** as the webhook gets only the data it needs to process and not the whole form data. And, multiple webhooks can call the API with different queries to get the data they need.

# Design

## `/form`

### `POST` - Create a form

#### Request

-   fields: `Array` of `Object` with `name` and `type` of the field
-   fields[].name: `String` name of the field
-   fields[].type: `String` type of the field - text/number
-   text field can have every form field which cannot be represented by a number

```json
{
    "name": "My Form",
    "description": "My Form Description",
    "fields": [
        {
            "name": "Name",
            "type": "text"
        },
        {
            "name": "Email",
            "type": "text"
        },
        {
            "name": "Phone",
            "type": "text"
        }
    ]
}
```

## `webhook`

### `POST` - Create a webhook

#### Request

```json
{
    "url": <webhook url>,
}
```

the app will make a `POST` request to the webhook url with submission id as the body.

## `/form/{form_id}`

### `POST` - Submit a form

#### Request

```json
{
    "name": "John Doe",
    "email": "johndoe@gmail.com",
    "phone": "1234567890"
}
```

## `/query`

### `POST` - Query the data

#### Request

```json
{
    "query": "(<form_id>) [name, tel] {name = Doe}"
}
```

## Query Language

Construct a SQL query from it.
This language can be extended to support more features.

### Syntax

```
(<form_id>) [<field_name>, <field_name>] {<field_name> = <regex>, <field_name> = <regex>}
```

or

```
/<submission_id>/ [<field_name>, <field_name>] {<field_name> = <regex>, <field_name> = <regex>}
```

-   last two brackets are optional
-   field_name between `[` and `]` are for selecting fields
-   field_name between `{` and `}` are for filtering

**returns json**

## FailSafe

-   We can have a load balancer in front of multiple API servers. If one server fails, the load balancer can route the request to another server.
-   If the webhook fails, we can retry it after a certain time interval. We can also have a retry limit after which we can remove the webhook.
