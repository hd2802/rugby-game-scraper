import { isFileEmpty } from "./utils/fileChecker.js"

const main = async () => {
    console.log("hello world")
    console.log(isFileEmpty("./data/french_data.txt"))
}

main()