import { useState, useEffect } from "react";
import axios from "axios";

const useServerStatus = (pingUrl = "/api/healthcheck/", intervalMs = 10000) => {
    const [isServerUp, setIsServerUp] = useState(true);

    useEffect(() => {
        const checkServer = async () => {
            try {
                await axios.get(pingUrl);
                setIsServerUp(true);
            } catch (error) {
                setIsServerUp(false);
            }
        };

        checkServer();
        const interval = setInterval(checkServer, intervalMs);
        return () => clearInterval(interval);
    }, [pingUrl, intervalMs]);

    return { isServerUp };
};

export default useServerStatus;
