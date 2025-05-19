import { render } from "@testing-library/react";
import { CoffeeProvider, CoffeeContext } from "../CoffeeContext";
import React from "react";
import { act } from "react-dom/test-utils";
import coffeeList from "../CoffeeList"; // Import the actual list

describe("CoffeeContext", () => {
    test("editCoffee updates an existing coffee", () => {
        let contextValue;

        render(
            <CoffeeProvider>
                <CoffeeContext.Consumer>
                    {value => {
                        contextValue = value;
                        return null;
                    }}
                </CoffeeContext.Consumer>
            </CoffeeProvider>
        );

        // Ensure initial state matches coffeeList
        expect(contextValue.coffees).toEqual(coffeeList);

        act(() => {
            contextValue.editCoffee({
                name: "Latte",
                origin: "France",
                description: "Now with extra foam!"
            });
        });

        // Expected result: Only the "Latte" description should change
        const expectedCoffees = coffeeList.map(coffee =>
            coffee.name === "Latte"
                ? { ...coffee, description: "Now with extra foam!" }
                : coffee
        );

        expect(contextValue.coffees).toEqual(expectedCoffees);
    });
});



// import { renderHook, act } from "@testing-library/react-hooks";
// import { CoffeeProvider, CoffeeContext } from "./CoffeeProvider";
//
// describe("CoffeeProvider", () => {
//     it("should initialize with default coffee list", () => {
//         const { result } = renderHook(() => CoffeeContext._currentValue, {
//             wrapper: CoffeeProvider,
//         });
//
//         expect(result.current.coffees).toHaveLength(16); // Check initial coffee list length
//         expect(result.current.coffees[0].name).toBe("Espresso"); // First item should be "Espresso"
//     });
//
//     it("should add a new coffee", () => {
//         const { result } = renderHook(() => CoffeeContext._currentValue, {
//             wrapper: CoffeeProvider,
//         });
//
//         act(() => {
//             result.current.addCoffee({
//                 name: "Turkish Coffee",
//                 origin: "Turkey",
//                 description: "Strong unfiltered coffee"
//             });
//         });
//
//         expect(result.current.coffees).toHaveLength(17);
//         expect(result.current.coffees.some(coffee => coffee.name === "Turkish Coffee")).toBe(true);
//     });
//
//     it("should edit an existing coffee", () => {
//         const { result } = renderHook(() => CoffeeContext._currentValue, {
//             wrapper: CoffeeProvider,
//         });
//
//         act(() => {
//             result.current.editCoffee({
//                 name: "Espresso",
//                 origin: "Italy",
//                 description: "Updated strong and bold coffee"
//             });
//         });
//
//         const updatedCoffee = result.current.coffees.find(coffee => coffee.name === "Espresso");
//         expect(updatedCoffee.description).toBe("Updated strong and bold coffee");
//     });
//
//     it("should delete a coffee by name", () => {
//         const { result } = renderHook(() => CoffeeContext._currentValue, {
//             wrapper: CoffeeProvider,
//         });
//
//         act(() => {
//             result.current.deleteCoffee("Latte");
//         });
//
//         expect(result.current.coffees).toHaveLength(15); // Latte should be removed
//         expect(result.current.coffees.some(coffee => coffee.name === "Latte")).toBe(false);
//     });
//
//     it("should not delete if coffee name does not exist", () => {
//         const { result } = renderHook(() => CoffeeContext._currentValue, {
//             wrapper: CoffeeProvider,
//         });
//
//         act(() => {
//             result.current.deleteCoffee("NonExistentCoffee");
//         });
//
//         expect(result.current.coffees).toHaveLength(16); // List remains unchanged
//     });
// });


