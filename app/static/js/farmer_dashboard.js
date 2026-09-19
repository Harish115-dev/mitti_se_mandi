(function () {

    /* =========================================
       FARMER DASHBOARD
       Flask + Jinja + MySQL version

       Real data currently used:
       - Farmer profile
       - Farmer crops

       Not connected yet:
       - Market prices
       - Buyer requests
       - Buyers
       - Orders
       ========================================= */


    /* ---------- DATA FROM FLASK ---------- */

    const fd = window.farmerData || {};
    const dbCrops = window.myCrops || [];


    /* ---------- APPLICATION STATE ---------- */

    const state = {

        farmer: {
            name: fd.name || "Farmer",
            village: fd.village || "Location",
            phone: fd.phone || "",
            crops: fd.crops || "Not set",
            since: fd.since || "2024",
            land: fd.land || "Not set"
        },


        /*
         * Real crop data from Flask / MySQL.
         */
        crops: dbCrops.map(function (c) {

            return {
                id: c.id,

                name: c.crop_name,

                qty: c.quantity,

                unit: c.quantity_unit || "quintal",

                grade: c.grade || "Not graded",

                price: Number(
                    c.price || 0
                ),

                status: (
                    c.status || "available"
                ).toLowerCase()
            };

        }),


        /*
         * These modules are intentionally empty.
         *
         * We will connect them to real Flask APIs
         * when their backend modules are implemented.
         */
        prices: [],

        requests: [],

        buyers: [],

        orders: [],


        priceFilter: "All"

    };


    /* =========================================
       NAVIGATION CONFIGURATION
       ========================================= */

    const nav = {

        dashboard: {
            label: "Dashboard",
            view: "dashboard"
        },

        "my-crops": {
            label: "My Crops",
            view: "my-crops"
        },

        "market-prices": {
            label: "Market Prices",
            view: "market-prices"
        },

        buyers: {
            label: "Buyers",
            view: "buyers"
        },

        orders: {
            label: "Orders",
            view: "orders"
        },

        profile: {
            label: "Profile",
            view: "profile"
        }

    };


    let activeGroup = "dashboard";

    let activeView = "dashboard";


    const viewToGroup = {

        dashboard: "dashboard",

        "my-crops": "my-crops",

        "market-prices": "market-prices",

        buyers: "buyers",

        "buyer-requests": "buyers",

        orders: "orders",

        profile: "profile",

        "edit-profile": "profile"

    };


    /* =========================================
       SIDEBAR
       ========================================= */

    const navList =
        document.getElementById(
            "navList"
        );


    if (navList) {

        Object.keys(nav).forEach(function (key) {

            const group = nav[key];


            const li =
                document.createElement("li");


            const button =
                document.createElement("button");


            button.className =
                "nav-btn"
                +
                (
                    key === activeGroup
                        ? " active"
                        : ""
                );


            button.textContent =
                group.label;


            button.addEventListener(
                "click",
                function () {

                    activeGroup = key;

                    goTo(group.view);

                    renderNav();

                }
            );


            li.appendChild(button);

            navList.appendChild(li);

        });

    }


    function renderNav() {

        document
            .querySelectorAll(".nav-btn")
            .forEach(function (button, index) {

                const key =
                    Object.keys(nav)[index];


                button.classList.toggle(
                    "active",
                    key === activeGroup
                );

            });

    }


    function goTo(id) {

        activeView = id;


        document
            .querySelectorAll(".view")
            .forEach(function (view) {

                view.classList.remove(
                    "active"
                );

            });


        const viewElement =
            document.getElementById(
                "view-" + id
            );


        if (viewElement) {

            viewElement.classList.add(
                "active"
            );

        }


        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });


        renderNav();

    }


    /* =========================================
       DATA-NAV LINKS
       ========================================= */

    document
        .querySelectorAll("[data-nav]")
        .forEach(function (element) {

            element.addEventListener(
                "click",
                function () {

                    const target =
                        element.getAttribute(
                            "data-nav"
                        );


                    activeGroup =
                        viewToGroup[target]
                        || target;


                    goTo(target);

                }
            );

        });


    /* =========================================
       TOAST
       ========================================= */

    function toast(message) {

        const toastElement =
            document.getElementById(
                "toast"
            );


        if (!toastElement) {
            return;
        }


        toastElement.textContent =
            message;


        toastElement.classList.add(
            "show"
        );


        clearTimeout(
            toastElement._tm
        );


        toastElement._tm =
            setTimeout(
                function () {

                    toastElement.classList.remove(
                        "show"
                    );

                },
                2200
            );

    }


    /* =========================================
       UNIT LABEL
       ========================================= */

    function unitLabel(unit) {

        if (!unit) {
            return "";
        }


        return String(unit);

    }


    /* =========================================
       STATUS CLASS
       ========================================= */

    function getStatusClass(status) {

        const normalized =
            String(
                status || ""
            ).toLowerCase();


        if (
            normalized === "available"
            ||
            normalized === "listed"
            ||
            normalized === "accepted"
        ) {

            return "pill-avail";

        }


        if (
            normalized === "pending"
            ||
            normalized === "draft"
        ) {

            return "pill-pending";

        }


        return "pill-sold";

    }


    /* =========================================
       DASHBOARD
       ========================================= */

    function renderDashboard() {

        const farmer =
            state.farmer;


        const nameParts =
            farmer.name
                .trim()
                .split(/\s+/);


        const initials =
            nameParts
                .map(function (word) {
                    return word.charAt(0);
                })
                .slice(0, 2)
                .join("");


        const topAvatar =
            document.getElementById(
                "topAv"
            );


        if (topAvatar) {

            topAvatar.textContent =
                initials || "F";

        }


        const topName =
            document.getElementById(
                "topName"
            );


        if (topName) {

            topName.textContent =
                farmer.name;

        }


        const logoInitial =
            document.getElementById(
                "logoInit"
            );


        if (logoInitial) {

            logoInitial.textContent =
                "M";

        }


        const greeting =
            document.getElementById(
                "greeting"
            );


        if (greeting) {

            greeting.textContent =
                `Good Morning, ${
                    nameParts[0] || "Farmer"
                }!`;

        }


        /* -------------------------------------
           REAL CROP STATISTICS
           ------------------------------------- */

        const totalCrops =
            state.crops.length;


        const activeListings =
            state.crops.filter(
                function (crop) {

                    return (
                        crop.status === "available"
                        ||
                        crop.status === "listed"
                    );

                }
            ).length;


        /*
         * Marketplace module is not implemented yet.
         * Never display fake order numbers.
         */
        const pendingOrders = 0;


        /*
         * Transaction module is not implemented yet.
         * Never display fake sales.
         */
        const totalSales = 0;


        const statGrid =
            document.getElementById(
                "statGrid"
            );


        if (statGrid) {

            statGrid.innerHTML = `

                <div class="stat-card">

                    <div class="stat-label">
                        Total Crops
                    </div>

                    <div class="stat-value">
                        ${totalCrops}
                    </div>

                    <div class="stat-note">
                        Currently listed
                    </div>

                </div>


                <div class="stat-card">

                    <div class="stat-label">
                        Active Listings
                    </div>

                    <div class="stat-value">
                        ${activeListings}
                    </div>

                    <div class="stat-note">
                        Available for sale
                    </div>

                </div>


                <div class="stat-card">

                    <div class="stat-label">
                        Pending Orders
                    </div>

                    <div class="stat-value">
                        ${pendingOrders}
                    </div>

                    <div class="stat-note">
                        Marketplace module pending
                    </div>

                </div>


                <div class="stat-card">

                    <div class="stat-label">
                        Total Sales
                    </div>

                    <div class="stat-value">
                        ₹${totalSales.toLocaleString(
                            "en-IN"
                        )}
                    </div>

                    <div class="stat-note">
                        Transaction module pending
                    </div>

                </div>

            `;

        }


        /* -------------------------------------
           FARMER CROPS
           ------------------------------------- */

        const dashCropList =
            document.getElementById(
                "dashCropList"
            );


        if (dashCropList) {

            if (!state.crops.length) {

                dashCropList.innerHTML = `
                    <div class="empty">
                        No crops listed yet.
                    </div>
                `;

            } else {

                dashCropList.innerHTML =
                    state.crops
                        .slice(0, 3)
                        .map(function (crop) {

                            return `

                                <div class="crop-row">

                                    <div>

                                        <div class="crop-name">
                                            ${crop.name}
                                        </div>

                                        <div class="crop-meta">

                                            ${
                                                crop.qty
                                            }

                                            ${
                                                unitLabel(
                                                    crop.unit
                                                )
                                            }

                                            ·

                                            ${
                                                crop.grade
                                            }

                                        </div>

                                    </div>


                                    <div
                                        style="
                                            text-align:right;
                                        "
                                    >

                                        <div class="crop-price">

                                            ${
                                                crop.price > 0
                                                    ? "₹" +
                                                      crop.price.toLocaleString(
                                                          "en-IN"
                                                      )
                                                    : "—"
                                            }

                                            ${
                                                crop.price > 0
                                                    ? "/" +
                                                      unitLabel(
                                                          crop.unit
                                                      )
                                                    : ""
                                            }

                                        </div>


                                        <span
                                            class="
                                                pill
                                                ${getStatusClass(
                                                    crop.status
                                                )}
                                            "
                                        >
                                            ${crop.status}
                                        </span>

                                    </div>

                                </div>

                            `;

                        })
                        .join("");

            }

        }


        /* -------------------------------------
           MARKET PRICE PREVIEW
           ------------------------------------- */

        const dashPriceList =
            document.getElementById(
                "dashPriceList"
            );


        if (dashPriceList) {

            if (!state.prices.length) {

                dashPriceList.innerHTML = `
                    <div class="empty">
                        Market price data will appear here
                        after the market API is connected.
                    </div>
                `;

            } else {

                dashPriceList.innerHTML =
                    state.prices
                        .slice(0, 4)
                        .map(function (price) {

                            return `

                                <div class="price-row">

                                    <div class="price-crop">
                                        ${price.crop}
                                    </div>

                                    <div class="price-right">

                                        <div class="price-val">
                                            ₹${Number(
                                                price.price
                                            ).toLocaleString(
                                                "en-IN"
                                            )}/${price.unit}
                                        </div>

                                        <div
                                            class="${
                                                price.trend === "up"
                                                    ? "change-up"
                                                    : "change-down"
                                            }"
                                        >

                                            ${
                                                price.trend === "up"
                                                    ? "▲"
                                                    : "▼"
                                            }

                                            ${price.change}

                                        </div>

                                    </div>

                                </div>

                            `;

                        })
                        .join("");

            }

        }


        /* -------------------------------------
           BUYER REQUESTS
           ------------------------------------- */

        const dashRequests =
            document.getElementById(
                "dashRequests"
            );


        if (dashRequests) {

            dashRequests.innerHTML =
                renderReqList(
                    state.requests.slice(0, 3)
                );


            bindReqButtons();

        }

    }


    /* =========================================
       REQUEST LIST
       ========================================= */

    function renderReqList(list) {

        if (!list.length) {

            return `
                <div class="empty">
                    No buyer requests yet.
                </div>
            `;

        }


        return list
            .map(function (request) {

                const initials =
                    request.buyer
                        .split(" ")
                        .map(function (word) {
                            return word[0];
                        })
                        .slice(0, 2)
                        .join("");


                return `

                    <div class="req-row">

                        <div
                            style="
                                display:flex;
                                align-items:center;
                                gap:12px;
                            "
                        >

                            <div class="req-av">
                                ${initials}
                            </div>

                            <div>

                                <div class="req-name">
                                    ${request.buyer}
                                </div>

                                <div class="req-meta">
                                    ${request.crop}
                                    ·
                                    ${request.qty}
                                    ·
                                    ${request.when}
                                </div>

                            </div>

                        </div>


                        <div
                            style="
                                display:flex;
                                gap:8px;
                                align-items:center;
                            "
                        >

                            <span
                                style="
                                    font-weight:700;
                                    font-size:0.9rem;
                                    margin-right:4px;
                                "
                            >
                                ${request.price}
                            </span>


                            ${
                                request.status === "pending"

                                ? `

                                    <button
                                        class="btn btn-primary btn-sm"
                                        data-acc="${request.id}"
                                    >
                                        Accept
                                    </button>

                                    <button
                                        class="btn btn-outline btn-sm"
                                        data-dec="${request.id}"
                                    >
                                        Decline
                                    </button>

                                `

                                :

                                `

                                    <span
                                        class="
                                            pill
                                            ${getStatusClass(
                                                request.status
                                            )}
                                        "
                                    >
                                        ${request.status}
                                    </span>

                                `
                            }

                        </div>

                    </div>

                `;

            })
            .join("");

    }


    /* =========================================
       REQUEST BUTTONS
       ========================================= */

    function bindReqButtons() {

        document
            .querySelectorAll(
                "[data-acc]"
            )
            .forEach(function (button) {

                button.addEventListener(
                    "click",
                    function () {

                        const request =
                            state.requests.find(
                                function (item) {

                                    return (
                                        item.id ==
                                        button.getAttribute(
                                            "data-acc"
                                        )
                                    );

                                }
                            );


                        if (request) {

                            request.status =
                                "accepted";


                            toast(
                                `Accepted request from ${request.buyer}`
                            );


                            renderAll();

                        }

                    }
                );

            });


        document
            .querySelectorAll(
                "[data-dec]"
            )
            .forEach(function (button) {

                button.addEventListener(
                    "click",
                    function () {

                        const request =
                            state.requests.find(
                                function (item) {

                                    return (
                                        item.id ==
                                        button.getAttribute(
                                            "data-dec"
                                        )
                                    );

                                }
                            );


                        if (request) {

                            request.status =
                                "declined";


                            toast(
                                `Declined request from ${request.buyer}`
                            );


                            renderAll();

                        }

                    }
                );

            });

    }


    /* =========================================
       CROPS
       ========================================= */

    function renderCrops(
        filter = ""
    ) {

        const normalizedFilter =
            filter
                .trim()
                .toLowerCase();


        const list =
            state.crops.filter(
                function (crop) {

                    return crop.name
                        .toLowerCase()
                        .includes(
                            normalizedFilter
                        );

                }
            );


        const grid =
            document.getElementById(
                "cropGrid"
            );


        if (!grid) {
            return;
        }


        if (!list.length) {

            grid.innerHTML = `

                <div class="empty">

                    ${
                        normalizedFilter
                            ? `No crops match "${filter}".`
                            : "No crops listed yet."
                    }

                </div>

            `;

            return;

        }


        grid.innerHTML =
            list
                .map(function (crop) {

                    return `

                        <div class="crop-tile">

                            <div class="ct-top">

                                <span class="crop-badge">

                                    ${
                                        crop.name
                                            .charAt(0)
                                            .toUpperCase()
                                    }

                                </span>


                                <span
                                    class="
                                        pill
                                        ${getStatusClass(
                                            crop.status
                                        )}
                                    "
                                >
                                    ${crop.status}
                                </span>

                            </div>


                            <div class="ct-name">
                                ${crop.name}
                            </div>


                            <div class="ct-row">

                                <span>
                                    Quantity
                                </span>

                                <span>
                                    ${crop.qty}
                                    ${unitLabel(crop.unit)}
                                </span>

                            </div>


                            <div class="ct-row">

                                <span>
                                    Grade
                                </span>

                                <span>
                                    ${crop.grade}
                                </span>

                            </div>


                            <div class="ct-row">

                                <span>
                                    Expected price
                                </span>

                                <span>

                                    ${
                                        crop.price > 0
                                            ? "₹" +
                                              crop.price.toLocaleString(
                                                  "en-IN"
                                              )
                                            : "Not set"
                                    }

                                </span>

                            </div>


                            <div class="ct-actions">

                                <!--
                                    Edit/Delete will be enabled
                                    after the crop CRUD API is built.
                                -->

                                <button
                                    class="
                                        btn
                                        btn-outline
                                        btn-sm
                                    "
                                    disabled
                                >
                                    Edit
                                </button>


                                <button
                                    class="
                                        btn
                                        btn-danger
                                        btn-sm
                                    "
                                    disabled
                                >
                                    Delete
                                </button>

                            </div>

                        </div>

                    `;

                })
                .join("");

    }


    /* =========================================
       CROP SEARCH
       ========================================= */

    const cropSearch =
        document.getElementById(
            "cropSearch"
        );


    if (cropSearch) {

        cropSearch.addEventListener(
            "input",
            function (event) {

                renderCrops(
                    event.target.value
                );

            }
        );

    }


    /* =========================================
       ADD CROP MODAL
       ========================================= */

    const openAddCrop =
        document.getElementById(
            "openAddCrop"
        );


    if (openAddCrop) {

        openAddCrop.addEventListener(
            "click",
            function () {

                const overlay =
                    document.getElementById(
                        "cropOverlay"
                    );


                if (overlay) {

                    overlay.classList.add(
                        "active"
                    );

                }

            }
        );

    }


    const openAddCrop2 =
        document.getElementById(
            "openAddCrop2"
        );


    if (openAddCrop2) {

        openAddCrop2.addEventListener(
            "click",
            function () {

                const overlay =
                    document.getElementById(
                        "cropOverlay"
                    );


                if (overlay) {

                    overlay.classList.add(
                        "active"
                    );

                }

            }
        );

    }


    const cancelCrop =
        document.getElementById(
            "cancelCrop"
        );


    if (cancelCrop) {

        cancelCrop.addEventListener(
            "click",
            function () {

                const overlay =
                    document.getElementById(
                        "cropOverlay"
                    );


                if (overlay) {

                    overlay.classList.remove(
                        "active"
                    );

                }

            }
        );

    }


    const cropOverlay =
        document.getElementById(
            "cropOverlay"
        );


    if (cropOverlay) {

        cropOverlay.addEventListener(
            "click",
            function (event) {

                if (
                    event.target.id ===
                    "cropOverlay"
                ) {

                    event.currentTarget.classList.remove(
                        "active"
                    );

                }

            }
        );

    }


    /* =========================================
       MARKET PRICES
       ========================================= */
/* =========================================
   MARKET PRICES + 7-DAY FORECAST
   ========================================= */

async function loadMarkets() {

    const marketSelect =
        document.getElementById("marketSelect");

    const commoditySelect =
        document.getElementById("commoditySelect");

    const forecastButton =
        document.getElementById("loadForecastBtn");

    const errorBox =
        document.getElementById("marketError");


    if (
        !marketSelect ||
        !commoditySelect ||
        !forecastButton
    ) {
        return;
    }


    marketSelect.innerHTML = `
        <option value="">
            Loading markets...
        </option>
    `;

    marketSelect.disabled = true;

    commoditySelect.innerHTML = `
        <option value="">
            Select commodity
        </option>
    `;

    commoditySelect.disabled = true;

    forecastButton.disabled = true;


    if (errorBox) {
        errorBox.textContent = "";
    }


    try {

        const response =
            await fetch("/api/markets/");


        if (!response.ok) {

            throw new Error(
                `Failed to load markets (${response.status})`
            );

        }


        const data =
            await response.json();


        const markets =
            Array.isArray(data.markets)
                ? data.markets
                : [];


        if (!markets.length) {

            throw new Error(
                "No markets were returned by the API."
            );

        }


        marketSelect.innerHTML = `
            <option value="">
                Select market
            </option>
        `;


        markets.forEach(function (market) {

            const option =
                document.createElement("option");


            /*
             * Our markets API may return either:
             *   "market name"
             * or an object containing market_name.
             */

            if (
                typeof market === "string"
            ) {

                option.value = market;

                option.textContent = market;

            } else {

                const name =
                    market.market_name ||
                    market.marketName ||
                    market.name ||
                    "";


                option.value = name;

                option.textContent = name;

            }


            if (option.value) {

                marketSelect.appendChild(
                    option
                );

            }

        });


        marketSelect.disabled = false;


    } catch (error) {

        console.error(
            "Market loading error:",
            error
        );


        marketSelect.innerHTML = `
            <option value="">
                Unable to load markets
            </option>
        `;


        if (errorBox) {

            errorBox.textContent =
                error.message;

        }

    }

}


async function loadCommodities(marketName) {

    const commoditySelect =
        document.getElementById(
            "commoditySelect"
        );

    const forecastButton =
        document.getElementById(
            "loadForecastBtn"
        );

    const errorBox =
        document.getElementById(
            "marketError"
        );


    if (
        !commoditySelect ||
        !forecastButton
    ) {
        return;
    }


    commoditySelect.innerHTML = `
        <option value="">
            Loading commodities...
        </option>
    `;


    commoditySelect.disabled = true;

    forecastButton.disabled = true;


    if (errorBox) {
        errorBox.textContent = "";
    }


    if (!marketName) {

        commoditySelect.innerHTML = `
            <option value="">
                Select commodity
            </option>
        `;

        return;

    }


    try {

        const url =
            `/api/markets/${encodeURIComponent(
                marketName
            )}/commodities`;


        const response =
            await fetch(url);


        if (!response.ok) {

            throw new Error(
                `Failed to load commodities (${response.status})`
            );

        }


        const data =
            await response.json();


        const commodities =
            Array.isArray(data.commodities)
                ? data.commodities
                : [];


        commoditySelect.innerHTML = `
            <option value="">
                Select commodity
            </option>
        `;


        commodities.forEach(
            function (commodity) {

                const option =
                    document.createElement(
                        "option"
                    );


                option.value =
                    commodity;


                option.textContent =
                    commodity;


                commoditySelect.appendChild(
                    option
                );

            }
        );


        commoditySelect.disabled =
            commodities.length === 0;


        if (!commodities.length) {

            if (errorBox) {

                errorBox.textContent =
                    "No commodities available for this market.";

            }

        }


    } catch (error) {

        console.error(
            "Commodity loading error:",
            error
        );


        commoditySelect.innerHTML = `
            <option value="">
                Unable to load commodities
            </option>
        `;


        if (errorBox) {

            errorBox.textContent =
                error.message;

        }

    }

}


function resetForecastDisplay() {

    const currentPrice =
        document.getElementById(
            "currentPrice"
        );

    const reportDate =
        document.getElementById(
            "reportDate"
        );

    const day7Price =
        document.getElementById(
            "day7Price"
        );

    const day7Date =
        document.getElementById(
            "day7Date"
        );

    const change7d =
        document.getElementById(
            "change7d"
        );

    const recommendation =
        document.getElementById(
            "recommendation"
        );

    const forecastTable =
        document.getElementById(
            "forecastTable"
        );


    if (currentPrice) {
        currentPrice.textContent = "—";
    }

    if (reportDate) {
        reportDate.textContent = "—";
    }

    if (day7Price) {
        day7Price.textContent = "—";
    }

    if (day7Date) {
        day7Date.textContent = "—";
    }

    if (change7d) {
        change7d.textContent = "—";
    }

    if (recommendation) {
        recommendation.textContent = "—";
    }


    if (forecastTable) {

        forecastTable.innerHTML = `

            <tr>
                <th>Day</th>
                <th>Date</th>
                <th>Predicted Price</th>
            </tr>

            <tr>
                <td colspan="3">
                    No forecast loaded.
                </td>
            </tr>

        `;

    }


    const summary =
        document.getElementById(
            "dashForecastSummary"
        );


    if (summary) {

        summary.textContent =
            "Select a market and commodity in Market Prices.";

        summary.classList.add("empty");

    }

}


async function loadForecast() {

    const marketSelect =
        document.getElementById(
            "marketSelect"
        );

    const commoditySelect =
        document.getElementById(
            "commoditySelect"
        );

    const errorBox =
        document.getElementById(
            "marketError"
        );

    const market =
        marketSelect
            ? marketSelect.value
            : "";

    const commodity =
        commoditySelect
            ? commoditySelect.value
            : "";


    if (!market || !commodity) {

        if (errorBox) {

            errorBox.textContent =
                "Please select both market and commodity.";

        }

        return;

    }


    if (errorBox) {
        errorBox.textContent = "";
    }


    resetForecastDisplay();


    const button =
        document.getElementById(
            "loadForecastBtn"
        );


    if (button) {

        button.disabled = true;

        button.textContent =
            "Loading...";

    }


    try {

        const url =
            `/api/forecast/?market=${encodeURIComponent(
                market
            )}&commodity=${encodeURIComponent(
                commodity
            )}`;


        const response =
            await fetch(url);


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.error ||
                "Failed to generate forecast."
            );

        }


        /* -------------------------------------
           CURRENT PRICE
           ------------------------------------- */

        const currentPrice =
            document.getElementById(
                "currentPrice"
            );


        const reportDate =
            document.getElementById(
                "reportDate"
            );


        if (currentPrice) {

            currentPrice.textContent =
                `₹${Number(
                    data.current_price
                ).toLocaleString(
                    "en-IN",
                    {
                        maximumFractionDigits: 2
                    }
                )}`;

        }


        if (reportDate) {

            reportDate.textContent =
                `Report date: ${
                    data.report_date
                }`;

        }


        /* -------------------------------------
           DAY 7
           ------------------------------------- */

        const day7 =
            data.forecast &&
            data.forecast.day_7;


        const day7Price =
            document.getElementById(
                "day7Price"
            );


        const day7Date =
            document.getElementById(
                "day7Date"
            );


        if (day7) {

            if (day7Price) {

                day7Price.textContent =
                    `₹${Number(
                        day7.price
                    ).toLocaleString(
                        "en-IN",
                        {
                            maximumFractionDigits: 2
                        }
                    )}`;

            }


            if (day7Date) {

                day7Date.textContent =
                    `For ${day7.date}`;

            }

        }


        /* -------------------------------------
           CHANGE
           ------------------------------------- */

        const change7d =
            document.getElementById(
                "change7d"
            );


        if (change7d) {

            const change =
                Number(
                    data.predicted_change_7d_pct
                );


            const sign =
                change > 0
                    ? "+"
                    : "";


            change7d.textContent =
                `${sign}${change.toFixed(2)}%`;


            change7d.classList.remove(
                "change-up",
                "change-down"
            );


            if (change > 0) {

                change7d.classList.add(
                    "change-up"
                );

            } else if (change < 0) {

                change7d.classList.add(
                    "change-down"
                );

            }

        }


        /* -------------------------------------
           RECOMMENDATION
           ------------------------------------- */

        const recommendation =
            document.getElementById(
                "recommendation"
            );


        if (recommendation) {

            recommendation.textContent =
                data.recommendation ||
                "NO STRONG SIGNAL";

        }


        /* -------------------------------------
           7-DAY FORECAST TABLE
           ------------------------------------- */

        const forecastTable =
            document.getElementById(
                "forecastTable"
            );


        if (forecastTable) {

            forecastTable.innerHTML = `

                <tr>

                    <th>
                        Day
                    </th>

                    <th>
                        Date
                    </th>

                    <th>
                        Predicted Price
                    </th>

                </tr>

            `;


            for (
                let day = 1;
                day <= 7;
                day++
            ) {

                const key =
                    `day_${day}`;


                const forecast =
                    data.forecast &&
                    data.forecast[key];


                if (!forecast) {
                    continue;
                }


                const row =
                    document.createElement(
                        "tr"
                    );


                row.innerHTML = `

                    <td>
                        Day ${day}
                    </td>

                    <td>
                        ${forecast.date}
                    </td>

                    <td>
                        ₹${Number(
                            forecast.price
                        ).toLocaleString(
                            "en-IN",
                            {
                                maximumFractionDigits: 2
                            }
                        )}
                    </td>

                `;


                forecastTable.appendChild(
                    row
                );

            }

        }


        /* -------------------------------------
           DASHBOARD FORECAST SUMMARY
           ------------------------------------- */

        const summary =
            document.getElementById(
                "dashForecastSummary"
            );


        if (summary) {

            summary.classList.remove(
                "empty"
            );


            summary.innerHTML = `

                <strong>
                    ${commodity}
                </strong>
                at
                <strong>
                    ${market}
                </strong>

                <br>

                Current:
                <strong>
                    ₹${Number(
                        data.current_price
                    ).toLocaleString(
                        "en-IN",
                        {
                            maximumFractionDigits: 2
                        }
                    )}
                </strong>

                →

                Day 7:
                <strong>
                    ₹${Number(
                        day7.price
                    ).toLocaleString(
                        "en-IN",
                        {
                            maximumFractionDigits: 2
                        }
                    )}
                </strong>

                <br>

                <strong>
                    ${data.predicted_change_7d_pct}%
                </strong>

                ·

                <strong>
                    ${data.recommendation}
                </strong>

            `;

        }


    } catch (error) {

        console.error(
            "Forecast error:",
            error
        );


        if (errorBox) {

            errorBox.textContent =
                error.message;

        }

    } finally {

        if (button) {

            button.disabled =
                !(
                    marketSelect &&
                    commoditySelect &&
                    marketSelect.value &&
                    commoditySelect.value
                );

            button.textContent =
                "Get Forecast";

        }

    }

}


function initializeMarketForecast() {

    const marketSelect =
        document.getElementById(
            "marketSelect"
        );

    const commoditySelect =
        document.getElementById(
            "commoditySelect"
        );

    const forecastButton =
        document.getElementById(
            "loadForecastBtn"
        );


    if (
        !marketSelect ||
        !commoditySelect ||
        !forecastButton
    ) {
        return;
    }


    marketSelect.addEventListener(
        "change",
        async function () {

            resetForecastDisplay();

            await loadCommodities(
                marketSelect.value
            );

        }
    );


    commoditySelect.addEventListener(
        "change",
        function () {

            forecastButton.disabled =
                !(
                    marketSelect.value &&
                    commoditySelect.value
                );

        }
    );


    forecastButton.addEventListener(
        "click",
        loadForecast
    );


    loadMarkets();

}

    /* =========================================
       BUYERS
       ========================================= */

    function renderBuyers() {

        const buyerGrid =
            document.getElementById(
                "buyerGrid"
            );


        if (!buyerGrid) {
            return;
        }


        if (!state.buyers.length) {

            buyerGrid.innerHTML = `

                <div class="empty">

                    Buyer marketplace will appear
                    after the buyer module is connected.

                </div>

            `;

            return;

        }


        buyerGrid.innerHTML =
            state.buyers
                .map(function (buyer) {

                    return `

                        <div class="crop-tile">

                            <div class="ct-top">

                                <span class="crop-badge">

                                    ${
                                        buyer.name
                                            .charAt(0)
                                            .toUpperCase()
                                    }

                                </span>


                                <span
                                    class="
                                        pill
                                        pill-pending
                                    "
                                >
                                    ★ ${buyer.rating}
                                </span>

                            </div>


                            <div class="ct-name">
                                ${buyer.name}
                            </div>


                            <div class="ct-row">

                                <span>
                                    Location
                                </span>

                                <span>
                                    ${buyer.loc}
                                </span>

                            </div>


                            <div class="ct-row">

                                <span>
                                    Buys
                                </span>

                                <span>
                                    ${buyer.deals}
                                </span>

                            </div>


                            <div class="ct-actions">

                                <button
                                    class="
                                        btn
                                        btn-primary
                                        btn-sm
                                    "
                                    data-contact="${buyer.name}"
                                >
                                    Contact
                                </button>

                            </div>

                        </div>

                    `;

                })
                .join("");


        document
            .querySelectorAll(
                "[data-contact]"
            )
            .forEach(function (button) {

                button.addEventListener(
                    "click",
                    function () {

                        toast(
                            `Buyer contact will be connected through the matching module.`
                        );

                    }
                );

            });

    }


    /* =========================================
       FULL REQUESTS
       ========================================= */

    function renderFullRequests() {

        const fullRequests =
            document.getElementById(
                "fullRequests"
            );


        if (!fullRequests) {
            return;
        }


        fullRequests.innerHTML =
            renderReqList(
                state.requests
            );


        bindReqButtons();

    }


    /* =========================================
       ORDERS
       ========================================= */

    function renderOrders() {

        const ordersTable =
            document.getElementById(
                "ordersTbl"
            );


        if (!ordersTable) {
            return;
        }


        if (!state.orders.length) {

            ordersTable.innerHTML = `

                <tr>

                    <td
                        colspan="7"
                        class="empty"
                    >

                        Orders will appear here
                        after the offer/transaction
                        workflow is implemented.

                    </td>

                </tr>

            `;

            return;

        }


        ordersTable.innerHTML = `

            <tr>

                <th>
                    Order ID
                </th>

                <th>
                    Crop
                </th>

                <th>
                    Buyer
                </th>

                <th>
                    Qty
                </th>

                <th>
                    Amount
                </th>

                <th>
                    Status
                </th>

                <th>
                    Date
                </th>

            </tr>


            ${
                state.orders
                    .map(function (order) {

                        return `

                            <tr>

                                <td>
                                    ${order.id}
                                </td>

                                <td>
                                    ${order.crop}
                                </td>

                                <td>
                                    ${order.buyer}
                                </td>

                                <td>
                                    ${order.qty}
                                </td>

                                <td>
                                    ${order.amount}
                                </td>

                                <td
                                    class="${
                                        order.status ===
                                        "Delivered"
                                            ? "change-up"
                                            : ""
                                    }"
                                >
                                    ${order.status}
                                </td>

                                <td>
                                    ${order.date}
                                </td>

                            </tr>

                        `;

                    })
                    .join("")
            }

        `;

    }


    /* =========================================
       PROFILE
       ========================================= */

    function renderProfile() {

        const profileView =
            document.getElementById(
                "profileView"
            );


        if (!profileView) {
            return;
        }


        const farmer =
            state.farmer;


        const initials =
            farmer.name
                .trim()
                .split(/\s+/)
                .map(function (word) {
                    return word[0];
                })
                .slice(0, 2)
                .join("");


        profileView.innerHTML = `

            <div class="p-av">
                ${initials}
            </div>


            <div class="p-row">

                <span>
                    Name
                </span>

                <span>
                    ${farmer.name}
                </span>

            </div>


            <div class="p-row">

                <span>
                    Village / District
                </span>

                <span>
                    ${farmer.village}
                </span>

            </div>


            <div class="p-row">

                <span>
                    Phone
                </span>

                <span>
                    ${farmer.phone || "Not provided"}
                </span>

            </div>


            <div class="p-row">

                <span>
                    Crops grown
                </span>

                <span>
                    ${farmer.crops || "Not set"}
                </span>

            </div>


            <div class="p-row">

                <span>
                    Land size
                </span>

                <span>
                    ${
                        farmer.land || "Not set"
                    }
                </span>

            </div>


            <div class="p-row">

                <span>
                    Member since
                </span>

                <span>
                    ${farmer.since}
                </span>

            </div>


            <div
                style="margin-top:20px;"
            >

                <button
                    class="btn btn-primary"
                    data-nav="edit-profile"
                >
                    Edit Profile
                </button>

            </div>

        `;


        profileView
            .querySelectorAll(
                "[data-nav]"
            )
            .forEach(function (element) {

                element.addEventListener(
                    "click",
                    function () {

                        activeGroup =
                            "profile";


                        goTo(
                            "edit-profile"
                        );

                    }
                );

            });

    }


    /* =========================================
       EDIT PROFILE
       ========================================= */

    function renderEditProfile() {

        const profileEdit =
            document.getElementById(
                "profileEdit"
            );


        if (!profileEdit) {
            return;
        }


        const farmer =
            state.farmer;


        profileEdit.innerHTML = `

            <div class="field">

                <label>
                    Name
                </label>

                <input
                    id="pfName"
                    value="${farmer.name}"
                >

            </div>


            <div class="field">

                <label>
                    Village / District
                </label>

                <input
                    id="pfVillage"
                    value="${farmer.village}"
                >

            </div>


            <div class="field">

                <label>
                    Phone
                </label>

                <input
                    id="pfPhone"
                    value="${farmer.phone}"
                >

            </div>


            <div class="field">

                <label>
                    Crops grown
                </label>

                <input
                    id="pfCrops"
                    value="${farmer.crops}"
                >

            </div>


            <div class="field">

                <label>
                    Land size
                </label>

                <input
                    id="pfLand"
                    value="${farmer.land}"
                >

            </div>


            <div
                class="modal-actions"
                style="
                    justify-content:flex-start;
                "
            >

                <button
                    class="btn btn-primary"
                    id="pfSave"
                >
                    Save changes
                </button>


                <button
                    class="btn btn-outline"
                    id="pfCancel"
                >
                    Cancel
                </button>

            </div>

        `;


        const saveButton =
            document.getElementById(
                "pfSave"
            );


        if (saveButton) {

            saveButton.addEventListener(
                "click",
                function () {

                    farmer.name =
                        document.getElementById(
                            "pfName"
                        ).value.trim()
                        || farmer.name;


                    farmer.village =
                        document.getElementById(
                            "pfVillage"
                        ).value.trim()
                        || farmer.village;


                    farmer.phone =
                        document.getElementById(
                            "pfPhone"
                        ).value.trim()
                        || farmer.phone;


                    farmer.crops =
                        document.getElementById(
                            "pfCrops"
                        ).value.trim()
                        || farmer.crops;


                    farmer.land =
                        document.getElementById(
                            "pfLand"
                        ).value.trim()
                        || farmer.land;


                    /*
                     * This is still local-only.
                     *
                     * We will connect it to a real
                     * Flask profile update route later.
                     */
                    toast(
                        "Profile updated locally."
                    );


                    activeGroup =
                        "profile";


                    goTo(
                        "profile"
                    );


                    renderAll();

                }
            );

        }


        const cancelButton =
            document.getElementById(
                "pfCancel"
            );


        if (cancelButton) {

            cancelButton.addEventListener(
                "click",
                function () {

                    activeGroup =
                        "profile";


                    goTo(
                        "profile"
                    );

                }
            );

        }

    }


    /* =========================================
       RENDER EVERYTHING
       ========================================= */

    function renderAll() {

    renderDashboard();

    const searchInput =
        document.getElementById(
            "cropSearch"
        );

    renderCrops(
        searchInput
            ? searchInput.value
            : ""
    );

    renderBuyers();

    renderFullRequests();

    renderOrders();

    renderProfile();

    renderEditProfile();
}


    /* =========================================
       MOBILE MENU
       ========================================= */

    const menuToggle =
        document.getElementById(
            "menuToggle"
        );


    if (menuToggle) {

        menuToggle.addEventListener(
            "click",
            function () {

                const sidebar =
                    document.querySelector(
                        ".sidebar"
                    );


                if (sidebar) {

                    sidebar.classList.toggle(
                        "collapsed"
                    );

                }

            }
        );

    }


       renderAll();
       
       renderNav();
       initializeMarketForecast();

})();