import got from "got";
import fastify from "fastify";

const url = "http://localhost:8000";

let response;

response = await got(`${url}/new-form/`, {
    method: "POST",
    json: {
        name: "My Form",
        description: "My Form Description",
        fields: [
            {
                name: "name",
                type: "text",
            },
            {
                name: "email",
                type: "text",
            },
            {
                name: "phone",
                type: "text",
            },
        ],
    },
});

console.log(response.body);

const form_info = JSON.parse(response.body);

console.log(form_info);

const form_fields_info = {};
for (const field of form_info.fields) {
    form_fields_info[field.name] = field.id;
}

const fields = Object.values(form_fields_info);
const form_id = form_info.form_id;

console.log(fields)

/*  SERVER  */

const server = fastify();

server.post("/", async (req, res) => {
    console.log(req.body);
    res.status(200);
});

server.listen({ port: 3000 });

/* REGISTER WEBHOOK */

got(`${url}/webhook/`, {
    method: "POST",
    json: {
        url: "http://localhost:3000",
        query: `(${form_id}) [${fields[0]}]`,
    },
})
    .then((res) => {
        console.log(res.body);
    })
    .catch(() => console.log("webhook failed to register"));

/* SUBMIT FORM */

const fake_data = [
    {
        name: "John Doe",
        email: "johndoe@gmail.com",
        phone: "+91 95658 27456",
    },
    {
        name: "Joe Doe",
        email: "joedoe@gmail.com",
        phone: "+91 97456 95658",
    },
];

let form_data = {};
form_data.form_id = form_id;

for (const fake in fake_data) {
    form_data.data = {};
    for (const [k, v] in Object.entries(fake)) {
        form_data.data[form_fields_info[k]] = v;
    }
    response = await got(`${url}/submit-form/`, {
        method: "POST",
        json: form_data,
    });
    console.log(response.body);
}
