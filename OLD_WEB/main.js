

let http = require('http');
let fs = require('fs');

let handleRequest = (request, response) => {
    response.writeHead(200, {
        'Content-Type': 'text/html'
    });
    fs.readFile('./index.html', null, function (error, data) {
        if (error) {
            response.writeHead(404);
            respone.write('File not found!');
        } else {
            response.write(data);
        }
        response.end();
    });
};
http.createServer(handleRequest).listen(8080); 


d3.csv("/data/Global_Landslide_Catalog_Export.csv", function(data) {
    console.log(data);
});
