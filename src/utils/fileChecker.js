import fs from 'fs'

export const isFileEmpty = (fileName) => {
    fs.readFile(fileName, function(err, data) {
        if (data.length == 0) {
            console.log("Empty")
        } else {
            console.log("Not empty")
        }
    })
}
