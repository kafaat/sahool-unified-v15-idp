import "reflect-metadata";
import { startFieldService } from "@sahool/field-shared";

const PORT = parseInt(process.env.PORT || "3000");
const SERVICE_NAME = "field-management-service";

startFieldService(SERVICE_NAME, PORT)
    .catch((error) => {
        console.error("❌ Failed to start field-management-service:", error);
        process.exit(1);
    });
