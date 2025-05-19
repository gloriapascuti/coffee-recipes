import {useEffect, useState} from "react";

const useNetworkStatus = () => {

    const [isOnline, setOnline] = useState<Boolean>(true);

    const updateNetworkStatus = () => {
        setOnline(navigator.onLine);
    }

    useEffect(() => {
        updateNetworkStatus()
        window.addEventListener("online", updateNetworkStatus);
        window.addEventListener("offline", updateNetworkStatus);

        return () => {
            window.removeEventListener("online", updateNetworkStatus);
            window.removeEventListener("offline", updateNetworkStatus);
        }
    }, []);

    return {isOnline};
}


export default useNetworkStatus;