const PENDING_OPERATIONS_KEY = 'pending_coffee_operations';
const LOCAL_COFFEES_KEY = 'local_coffees';

export const OfflineService = {
    // Save pending operations to local storage
    savePendingOperation: (operation) => {
        const operations = JSON.parse(localStorage.getItem(PENDING_OPERATIONS_KEY) || '[]');
        operations.push({
            ...operation,
            timestamp: new Date().toISOString(),
            retryCount: 0
        });
        localStorage.setItem(PENDING_OPERATIONS_KEY, JSON.stringify(operations));
    },

    // Get all pending operations
    getPendingOperations: () => {
        return JSON.parse(localStorage.getItem(PENDING_OPERATIONS_KEY) || '[]');
    },

    // Clear pending operations
    clearPendingOperations: () => {
        localStorage.removeItem(PENDING_OPERATIONS_KEY);
    },

    // Save local coffees
    saveLocalCoffees: (coffees) => {
        localStorage.setItem(LOCAL_COFFEES_KEY, JSON.stringify(coffees));
    },

    // Get local coffees
    getLocalCoffees: () => {
        return JSON.parse(localStorage.getItem(LOCAL_COFFEES_KEY) || '[]');
    },

    // Process pending operations when back online
    processPendingOperations: async (apiFunctions) => {
        const operations = OfflineService.getPendingOperations();
        if (operations.length === 0) return;

        const successfulOperations = [];
        const failedOperations = [];

        for (const operation of operations) {
            try {
                // Skip operations that have been retried too many times
                if (operation.retryCount >= 3) {
                    console.warn(`Operation ${operation.type} with id ${operation.id} failed too many times, skipping`);
                    continue;
                }

                switch (operation.type) {
                    case 'ADD':
                        await apiFunctions.addCoffee(operation.data);
                        successfulOperations.push(operation);
                        break;
                    case 'EDIT':
                        try {
                            await apiFunctions.editCoffee(operation.id, operation.data);
                            successfulOperations.push(operation);
                        } catch (error) {
                            // If edit fails because item doesn't exist, try adding it
                            if (error.message.includes('404')) {
                                await apiFunctions.addCoffee(operation.data);
                                successfulOperations.push(operation);
                            } else {
                                throw error;
                            }
                        }
                        break;
                    case 'DELETE':
                        try {
                            await apiFunctions.deleteCoffee(operation.id);
                            successfulOperations.push(operation);
                        } catch (error) {
                            // If delete fails because item doesn't exist, consider it successful
                            if (error.message.includes('404')) {
                                successfulOperations.push(operation);
                            } else {
                                throw error;
                            }
                        }
                        break;
                }
            } catch (error) {
                console.warn(`Failed to process operation:`, operation, error);
                // Increment retry count
                operation.retryCount = (operation.retryCount || 0) + 1;
                failedOperations.push(operation);
            }
        }

        // Update pending operations with retry counts
        localStorage.setItem(PENDING_OPERATIONS_KEY, JSON.stringify(failedOperations));
    }
}; 