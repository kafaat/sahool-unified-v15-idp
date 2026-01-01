import "reflect-metadata";
import { startFieldService } from "@sahool/field-shared";

const PORT = parseInt(process.env.PORT || "3000");
const SERVICE_NAME = "field-core";

startFieldService(SERVICE_NAME, PORT)
    .catch((error) => {
        console.error("❌ Failed to start field-core service:", error);
        process.exit(1);
    });
