
(function () {
    "use strict";


    /* =====================================================
       SERVER DATA
    ====================================================== */

    const farmer = window.farmerData || {};

    const crops = Array.isArray(window.myCrops)
        ? window.myCrops
        : [];


    /* =====================================================
       NAVIGATION
    ====================================================== */

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
        externalUrl: "/buyer-requirements/farmer"
        },

        offers: {
            label: "Offers",
            externalUrl: "/offers/farmer"
        },

        orders: {
            label: "Orders",
            externalUrl: "/transactions/farmer"
        },

        profile: {
            label: "Profile",
            view: "profile"
        }
    };


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


    let activeGroup = "dashboard";


    /* =====================================================
       HELPERS
    ====================================================== */

    const $ = (id) => {
        return document.getElementById(id);
    };


    function toast(message) {

        const element = $("toast");

        if (!element) {
            return;
        }

        element.textContent = message;

        element.classList.add("show");

        clearTimeout(element._timer);

        element._timer = setTimeout(() => {
            element.classList.remove("show");
        }, 2200);
    }


    function formatMoney(value) {

        const number = Number(value);

        if (!Number.isFinite(number)) {
            return "—";
        }

        return `₹${number.toLocaleString("en-IN", {
            maximumFractionDigits: 2
        })}`;
    }


    function initials(name) {

        return (
            String(name || "Farmer")
                .split(/\s+/)
                .filter(Boolean)
                .slice(0, 2)
                .map((word) => word[0].toUpperCase())
                .join("")
            || "F"
        );
    }


    function normalizedStatus(status) {

        return String(status || "")
            .trim()
            .toLowerCase();
    }


    function cropStatusClass(status) {

        const normalized = normalizedStatus(status);

        if (normalized === "available") {
            return "pill-avail";
        }

        if (normalized === "sold") {
            return "pill-sold";
        }

        return "pill-pending";
    }


    function escapeHtml(value) {

        const element = document.createElement("div");

        element.textContent = String(value ?? "");

        return element.innerHTML;
    }


    /* =====================================================
       NAVIGATION
    ====================================================== */

    function renderNav() {

        const navList = $("navList");

        if (!navList) {
            return;
        }

        navList.innerHTML = "";


        Object.entries(nav).forEach(([key, item]) => {

            const li = document.createElement("li");

            const button = document.createElement("button");

            button.type = "button";

            button.className =
                `nav-btn${key === activeGroup ? " active" : ""}`;

            button.textContent = item.label;


            button.addEventListener("click", () => {

                /* External Flask route */
                if (item.externalUrl) {

                    window.location.href =
                        item.externalUrl;

                    return;
                }


                activeGroup = key;

                goTo(item.view);
            });


            li.appendChild(button);

            navList.appendChild(li);
        });
    }


    function goTo(viewId) {

        document
            .querySelectorAll(".view")
            .forEach((view) => {
                view.classList.remove("active");
            });


        const target = $(`view-${viewId}`);


        if (!target) {
            console.warn(
                `Dashboard view not found: ${viewId}`
            );

            return;
        }


        target.classList.add("active");


        activeGroup =
            viewToGroup[viewId] || viewId;


        renderNav();


        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });


        /* Close mobile sidebar */
        const sidebar =
            document.querySelector(".sidebar");

        if (sidebar) {
            sidebar.classList.remove("collapsed");
        }


        const menuToggle =
            $("menuToggle");

        if (menuToggle) {
            menuToggle.classList.remove("active");
        }
    }


    function bindNavigation() {

        document
            .querySelectorAll("[data-nav]")
            .forEach((element) => {

                element.addEventListener(
                    "click",
                    () => {

                        const target =
                            element.getAttribute(
                                "data-nav"
                            );

                        if (target) {
                            goTo(target);
                        }
                    }
                );

            });
    }


    /* =====================================================
       HEADER
    ====================================================== */

    function renderHeader() {

        const name =
            farmer.full_name || "Farmer";


        const firstName =
            name.split(/\s+/)[0] || "Farmer";


        const avatar =
            initials(name).slice(0, 2);


        if ($("topAv")) {

            $("topAv").textContent =
                avatar;
        }


        if ($("topName")) {

            $("topName").textContent =
                name;
        }


        if ($("greeting")) {

            $("greeting").textContent =
                `Good Day, ${firstName}!`;
        }


        if ($("weatherPlace")) {

            const location = [
                farmer.city,
                farmer.state
            ]
                .filter(Boolean)
                .join(", ");


            $("weatherPlace").textContent =
                location || "Your location";
        }
    }


    /* =====================================================
       DASHBOARD STATS
    ====================================================== */

    function renderDashboardStats() {

        const totalCrops =
            crops.length;


        const activeListings =
            crops.filter(
                (crop) =>
                    normalizedStatus(
                        crop.status
                    ) === "available"
            ).length;


        const listedCrops =
            crops.filter(
                (crop) =>
                    normalizedStatus(
                        crop.status
                    ) === "listed"
            ).length;


        if (!$("statGrid")) {
            return;
        }


        $("statGrid").innerHTML = `

            <div class="stat-card">

                <div class="stat-label">
                    Total Crops
                </div>

                <div class="stat-value">
                    ${totalCrops}
                </div>

                <div class="stat-note">
                    Currently recorded
                </div>

            </div>


            <div class="stat-card">

                <div class="stat-label">
                    Available Crops
                </div>

                <div class="stat-value">
                    ${activeListings}
                </div>

                <div class="stat-note">
                    Available for marketplace
                </div>

            </div>


            <div class="stat-card">

                <div class="stat-label">
                    Published Listings
                </div>

                <div class="stat-value">
                    ${listedCrops}
                </div>

                <div class="stat-note">
                    Currently on marketplace
                </div>

            </div>


            <div class="stat-card">

                <div class="stat-label">
                    Total Sales
                </div>

                <div class="stat-value">
                    —
                </div>

                <div class="stat-note">
                    Transaction phase
                </div>

            </div>

        `;
    }


    /* =====================================================
       DASHBOARD CROP PREVIEW
    ====================================================== */

    function renderDashboardCrops() {

        const container =
            $("dashCropList");


        if (!container) {
            return;
        }


        if (!crops.length) {

            container.innerHTML = `
                <div class="empty">
                    No crops listed yet.
                </div>
            `;

            return;
        }


        container.innerHTML =
            crops
                .slice(0, 3)
                .map((crop) => {

                    const status =
                        normalizedStatus(
                            crop.status
                        );


                    const canPublish =
                        status === "available" &&
                        crop.id;


                    return `

                        <div class="crop-row">

                            <div>

                                <div class="crop-name">
                                    ${escapeHtml(
                                        crop.crop_name ||
                                        "Crop"
                                    )}
                                </div>

                                <div class="crop-meta">

                                    ${escapeHtml(
                                        String(
                                            crop.quantity ??
                                            "—"
                                        )
                                    )}

                                    Quintal

                                    ·

                                    ${escapeHtml(
                                        crop.grade ||
                                        "Not graded"
                                    )}

                                </div>

                            </div>


                            <div style="text-align:right;">

                                <div class="crop-price">

                                    ${formatMoney(
                                        crop.price
                                    )}/Quintal

                                </div>


                                <span
                                    class="
                                        pill
                                        ${cropStatusClass(
                                            crop.status
                                        )}
                                    "
                                >

                                    ${escapeHtml(
                                        crop.status ||
                                        "Unknown"
                                    )}

                                </span>


                                ${
                                    canPublish

                                        ? `

                                            <div
                                                style="
                                                    margin-top:8px;
                                                "
                                            >

                                                <form
                                                    action="/lots/publish/${encodeURIComponent(
                                                        crop.id
                                                    )}"
                                                    method="POST"
                                                    onsubmit="
                                                        return confirm(
                                                            'Publish this crop to the marketplace?'
                                                        );
                                                    "
                                                >

                                                    <button
                                                        type="submit"
                                                        class="btn btn-primary btn-small"
                                                    >
                                                        Publish
                                                    </button>

                                                </form>

                                            </div>

                                        `

                                        : ""

                                }

                            </div>

                        </div>

                    `;
                })
                .join("");
    }


    /* =====================================================
       MY CROPS
    ====================================================== */

    function renderCrops(filter = "") {

        const grid =
            $("cropGrid");


        if (!grid) {
            return;
        }


        const query =
            filter.trim().toLowerCase();


        const filtered =
            crops.filter((crop) => {

                const cropName =
                    String(
                        crop.crop_name || ""
                    )
                        .toLowerCase();


                return cropName.includes(query);
            });


        if (!filtered.length) {

            grid.innerHTML = `
                <div class="empty">
                    No crops match your search.
                </div>
            `;

            return;
        }


        grid.innerHTML =
            filtered
                .map((crop) => {

                    const status =
                        normalizedStatus(
                            crop.status
                        );


                    const canPublish =
                        status === "available" &&
                        crop.id;


                    return `

                        <div class="crop-tile">

                            <!-- HEADER -->

                            <div class="ct-top">

                                <span class="crop-badge">

                                    ${escapeHtml(
                                        String(
                                            crop.crop_name ||
                                            "C"
                                        )
                                            .charAt(0)
                                            .toUpperCase()
                                    )}

                                </span>


                                <span
                                    class="
                                        pill
                                        ${cropStatusClass(
                                            crop.status
                                        )}
                                    "
                                >

                                    ${escapeHtml(
                                        crop.status ||
                                        "Unknown"
                                    )}

                                </span>

                            </div>


                            <!-- NAME -->

                            <div class="ct-name">

                                ${escapeHtml(
                                    crop.crop_name ||
                                    "Crop"
                                )}

                            </div>


                            <!-- QUANTITY -->

                            <div class="ct-row">

                                <span>
                                    Quantity
                                </span>

                                <span>

                                    ${escapeHtml(
                                        String(
                                            crop.quantity ??
                                            "—"
                                        )
                                    )}

                                    Quintal

                                </span>

                            </div>


                            <!-- GRADE -->

                            <div class="ct-row">

                                <span>
                                    Grade
                                </span>

                                <span>

                                    ${escapeHtml(
                                        crop.grade ||
                                        "—"
                                    )}

                                </span>

                            </div>


                            <!-- PRICE -->

                            <div class="ct-row">

                                <span>
                                    Price
                                </span>

                                <span>

                                    ${formatMoney(
                                        crop.price
                                    )}/Quintal

                                </span>

                            </div>


                            <!-- MARKETPLACE ACTION -->

                            ${
                                canPublish

                                    ? `

                                        <div class="ct-actions">

                                            <form
                                                action="/lots/publish/${encodeURIComponent(
                                                    crop.id
                                                )}"
                                                method="POST"
                                                onsubmit="
                                                    return confirm(
                                                        'Publish this crop to the marketplace?'
                                                    );
                                                "
                                            >

                                                <button
                                                    type="submit"
                                                    class="btn btn-primary btn-small"
                                                >
                                                    Publish to Marketplace
                                                </button>

                                            </form>

                                        </div>

                                    `

                                    : `

                                        <div class="ct-actions">

                                            <span
                                                class="marketplace-state"
                                            >

                                                ${
                                                    status ===
                                                    "listed"

                                                        ? "Published on marketplace"

                                                        : status ===
                                                          "sold"

                                                            ? "Crop sold"

                                                            : status ===
                                                              "inactive"

                                                                ? "Inactive"

                                                                : "Unavailable"
                                                }

                                            </span>

                                        </div>

                                    `
                            }

                        </div>

                    `;
                })
                .join("");
    }


    /* =====================================================
       PROFILE
    ====================================================== */

    function renderProfile() {

        const profile =
            $("profileView");


        if (!profile) {
            return;
        }


        const location = [
            farmer.city,
            farmer.state
        ]
            .filter(Boolean)
            .join(", ") || "Not set";


        const initialsText =
            initials(farmer.full_name);


        profile.innerHTML = `

            <div class="p-av">
                ${escapeHtml(initialsText)}
            </div>


            <div class="p-row">

                <span>
                    Name
                </span>

                <span>
                    ${escapeHtml(
                        farmer.full_name ||
                        "—"
                    )}
                </span>

            </div>


            <div class="p-row">

                <span>
                    Email
                </span>

                <span>
                    ${escapeHtml(
                        farmer.email ||
                        "—"
                    )}
                </span>

            </div>


            <div class="p-row">

                <span>
                    Village / District
                </span>

                <span>
                    ${escapeHtml(
                        location
                    )}
                </span>

            </div>


            <div class="p-row">

                <span>
                    Phone
                </span>

                <span>
                    ${escapeHtml(
                        farmer.phone ||
                        "—"
                    )}
                </span>

            </div>


            <div class="p-row">

                <span>
                    Crops grown
                </span>

                <span>
                    ${escapeHtml(
                        farmer.crops ||
                        "Not set"
                    )}
                </span>

            </div>


            <div class="p-row">

                <span>
                    Land size
                </span>

                <span>
                    ${escapeHtml(
                        String(
                            farmer.land_size ??
                            "Not set"
                        )
                    )}
                </span>

            </div>


            <div class="p-row">

                <span>
                    Member since
                </span>

                <span>
                    ${escapeHtml(
                        String(
                            farmer.created_at ||
                            "—"
                        )
                    )}
                </span>

            </div>


            <div style="margin-top:20px;">

                <button
                    class="btn btn-primary"
                    data-nav="edit-profile"
                    type="button"
                >
                    Edit Profile
                </button>

            </div>

        `;


        const editButton =
            profile.querySelector(
                "[data-nav='edit-profile']"
            );


        if (editButton) {

            editButton.addEventListener(
                "click",
                () => {
                    goTo("edit-profile");
                }
            );
        }
    }


    function renderEditProfile() {

        const profileEdit =
            $("profileEdit");


        if (!profileEdit) {
            return;
        }


        const location = [
            farmer.city,
            farmer.state
        ]
            .filter(Boolean)
            .join(", ");


        profileEdit.innerHTML = `

            <div class="field">

                <label>
                    Name
                </label>

                <input
                    value="${escapeHtml(
                        farmer.full_name ||
                        ""
                    )}"
                    disabled
                >

            </div>


            <div class="field">

                <label>
                    Village / District
                </label>

                <input
                    value="${escapeHtml(
                        location
                    )}"
                    disabled
                >

            </div>


            <div class="field">

                <label>
                    Phone
                </label>

                <input
                    value="${escapeHtml(
                        farmer.phone ||
                        ""
                    )}"
                    disabled
                >

            </div>


            <div class="field">

                <label>
                    Email
                </label>

                <input
                    value="${escapeHtml(
                        farmer.email ||
                        ""
                    )}"
                    disabled
                >

            </div>


            <div
                class="empty"
                style="padding:20px 0 0;"
            >
                Profile editing will be added with
                the backend profile-update route.
            </div>

        `;
    }


    /* =====================================================
       MARKET API
    ====================================================== */

    async function loadMarkets() {

        const marketSelect =
            $("marketSelect");


        if (!marketSelect) {
            return;
        }


        marketSelect.innerHTML = `
            <option value="">
                Loading markets...
            </option>
        `;


        try {

            const response =
                await fetch(
                    "/api/markets/"
                );


            const data =
                await response.json();


            if (!response.ok) {

                throw new Error(
                    data.error ||
                    "Failed to load markets"
                );
            }


            marketSelect.innerHTML = `
                <option value="">
                    Select market
                </option>
            `;


            const markets =
                Array.isArray(data.markets)
                    ? data.markets
                    : [];


            markets.forEach((market) => {

                const option =
                    document.createElement(
                        "option"
                    );


                option.value =
                    market;


                option.textContent =
                    market;


                marketSelect.appendChild(
                    option
                );

            });

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


            if ($("marketError")) {

                $("marketError").textContent =
                    error.message;
            }
        }
    }


    async function loadCommodities() {

        const market =
            $("marketSelect").value;


        const commoditySelect =
            $("commoditySelect");


        const button =
            $("loadForecastBtn");


        commoditySelect.disabled = true;

        button.disabled = true;


        $("marketError").textContent = "";


        if (!market) {

            commoditySelect.innerHTML = `
                <option value="">
                    Select market first
                </option>
            `;

            return;
        }


        commoditySelect.innerHTML = `
            <option value="">
                Loading commodities...
            </option>
        `;


        try {

            const response =
                await fetch(
                    `/api/markets/${encodeURIComponent(
                        market
                    )}/commodities`
                );


            const data =
                await response.json();


            if (!response.ok) {

                throw new Error(
                    data.error ||
                    "Failed to load commodities"
                );
            }


            commoditySelect.innerHTML = `
                <option value="">
                    Select commodity
                </option>
            `;


            const commodities =
                Array.isArray(
                    data.commodities
                )
                    ? data.commodities
                    : [];


            commodities.forEach(
                (commodity) => {

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
                false;


            updateForecastButton();

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


            $("marketError").textContent =
                error.message;
        }
    }


    function updateForecastButton() {

        const market =
            $("marketSelect");


        const commodity =
            $("commoditySelect");


        const button =
            $("loadForecastBtn");


        if (!market || !commodity || !button) {
            return;
        }


        button.disabled =
            !(
                market.value &&
                commodity.value
            );
    }


    async function loadForecast() {

        const market =
            $("marketSelect").value;


        const commodity =
            $("commoditySelect").value;


        const button =
            $("loadForecastBtn");


        if (!market || !commodity) {
            return;
        }


        button.disabled = true;

        button.textContent =
            "Loading...";


        $("marketError").textContent =
            "";


        try {

            const response =
                await fetch(
                    `/api/forecast/?market=${encodeURIComponent(
                        market
                    )}&commodity=${encodeURIComponent(
                        commodity
                    )}`
                );


            const data =
                await response.json();


            if (!response.ok) {

                throw new Error(
                    data.error ||
                    "Failed to generate forecast"
                );
            }


            renderForecast(data);

        } catch (error) {

            console.error(
                "Forecast error:",
                error
            );


            $("marketError").textContent =
                error.message;

        } finally {

            button.textContent =
                "Get Forecast";


            updateForecastButton();
        }
    }


    /* =====================================================
       FORECAST
    ====================================================== */

    function renderForecast(data) {

        if (!data) {
            return;
        }


        const current =
            Number(
                data.current_price
            );


        const day7 =
            Number(
                data.forecast?.day_7?.price
            );


        const change =
            Number(
                data.predicted_change_7d_pct
            );


        $("currentPrice").textContent =
            formatMoney(current);


        $("reportDate").textContent =
            `Latest report: ${
                data.report_date || "—"
            }`;


        $("day7Price").textContent =
            formatMoney(day7);


        $("day7Date").textContent =
            data.forecast?.day_7?.date ||
            "—";


        $("change7d").textContent =
            Number.isFinite(change)

                ? `${
                    change >= 0
                        ? "+"
                        : ""
                }${change.toFixed(2)}%`

                : "—";


        $("recommendation").textContent =
            data.recommendation ||
            "NO STRONG SIGNAL";


        /* Change color */

        if (Number.isFinite(change)) {

            if (change > 0) {

                $("change7d").style.color =
                    "var(--positive)";

            } else if (change < 0) {

                $("change7d").style.color =
                    "var(--negative)";

            } else {

                $("change7d").style.color =
                    "var(--ink)";
            }

        }


        /* Recommendation color */

        if (data.recommendation === "SELL") {

            $("recommendation").style.color =
                "var(--negative)";

        } else if (
            data.recommendation === "HOLD"
        ) {

            $("recommendation").style.color =
                "var(--positive)";

        } else {

            $("recommendation").style.color =
                "var(--forest)";
        }


        /* Dashboard summary */

        if ($("dashForecastSummary")) {

            const changeClass =
                change >= 0
                    ? "change-up"
                    : "change-down";


            const arrow =
                change >= 0
                    ? "▲"
                    : "▼";


            $("dashForecastSummary").innerHTML = `

                <div class="price-row">

                    <div>

                        <div class="price-crop">

                            ${escapeHtml(
                                data.commodity ||
                                "Commodity"
                            )}

                        </div>


                        <div class="price-market">

                            ${escapeHtml(
                                data.market ||
                                "Market"
                            )}

                        </div>

                    </div>


                    <div class="price-right">

                        <div class="price-val">

                            ${formatMoney(day7)}

                        </div>


                        <div
                            class="${changeClass}"
                        >

                            ${arrow}

                            ${Math.abs(
                                change
                            ).toFixed(2)}%

                            in 7 days

                        </div>

                    </div>

                </div>


                <div
                    class="empty"
                    style="padding:18px 0 0;"
                >

                    Recommendation:

                    <strong>
                        ${escapeHtml(
                            data.recommendation ||
                            "NO STRONG SIGNAL"
                        )}
                    </strong>

                </div>

            `;
        }


        /* Forecast table */

        const forecast =
            data.forecast || {};


        $("forecastTable").innerHTML = `

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


            ${Object.entries(forecast)
                .map(
                    ([day, value]) => {

                        return `

                            <tr>

                                <td>
                                    ${escapeHtml(
                                        String(day)
                                            .replace(
                                                "day_",
                                                "Day "
                                            )
                                    )}
                                </td>


                                <td>
                                    ${escapeHtml(
                                        value?.date ||
                                        "—"
                                    )}
                                </td>


                                <td>
                                    ${formatMoney(
                                        value?.price
                                    )}
                                </td>

                            </tr>

                        `;
                    }
                )
                .join("")}

        `;
    }


    /* =====================================================
       CROP MODAL
    ====================================================== */

    function openCropModal() {

        const overlay =
            $("cropOverlay");


        if (!overlay) {
            return;
        }


        overlay.classList.add(
            "active"
        );
    }


    function closeCropModal() {

        const overlay =
            $("cropOverlay");


        if (!overlay) {
            return;
        }


        overlay.classList.remove(
            "active"
        );
    }


    /* =====================================================
       MOBILE MENU
    ====================================================== */

    function toggleMobileMenu() {

        const sidebar =
            document.querySelector(
                ".sidebar"
            );


        const menuToggle =
            $("menuToggle");


        if (!sidebar || !menuToggle) {
            return;
        }


        sidebar.classList.toggle(
            "collapsed"
        );


        menuToggle.classList.toggle(
            "active"
        );
    }


    /* =====================================================
       INITIALIZATION
    ====================================================== */

    function init() {

        /* Header */
        renderHeader();


        /* Dashboard */
        renderDashboardStats();

        renderDashboardCrops();


        /* Crops */
        renderCrops();


        /* Profile */
        renderProfile();

        renderEditProfile();


        /* Navigation */
        renderNav();

        bindNavigation();


        /* =================================================
           CROP SEARCH
        ================================================= */

        const cropSearch =
            $("cropSearch");


        if (cropSearch) {

            cropSearch.addEventListener(
                "input",
                (event) => {

                    renderCrops(
                        event.target.value
                    );

                }
            );
        }


        /* =================================================
           ADD CROP
        ================================================= */

        const openAddCrop =
            $("openAddCrop");


        if (openAddCrop) {

            openAddCrop.addEventListener(
                "click",
                openCropModal
            );
        }


        const openAddCrop2 =
            $("openAddCrop2");


        if (openAddCrop2) {

            openAddCrop2.addEventListener(
                "click",
                openCropModal
            );
        }


        /* =================================================
           CANCEL CROP
        ================================================= */

        const cancelCrop =
            $("cancelCrop");


        if (cancelCrop) {

            cancelCrop.addEventListener(
                "click",
                closeCropModal
            );
        }


        /* =================================================
           CLOSE MODAL ON OVERLAY
        ================================================= */

        const cropOverlay =
            $("cropOverlay");


        if (cropOverlay) {

            cropOverlay.addEventListener(
                "click",
                (event) => {

                    if (
                        event.target ===
                        cropOverlay
                    ) {

                        closeCropModal();
                    }
                }
            );
        }


        /* =================================================
           MARKET SELECT
        ================================================= */

        const marketSelect =
            $("marketSelect");


        if (marketSelect) {

            marketSelect.addEventListener(
                "change",
                loadCommodities
            );
        }


        /* =================================================
           COMMODITY SELECT
        ================================================= */

        const commoditySelect =
            $("commoditySelect");


        if (commoditySelect) {

            commoditySelect.addEventListener(
                "change",
                updateForecastButton
            );
        }


        /* =================================================
           FORECAST BUTTON
        ================================================= */

        const loadForecastBtn =
            $("loadForecastBtn");


        if (loadForecastBtn) {

            loadForecastBtn.addEventListener(
                "click",
                loadForecast
            );
        }


        /* =================================================
           MOBILE MENU
        ================================================= */

        const menuToggle =
            $("menuToggle");


        if (menuToggle) {

            menuToggle.addEventListener(
                "click",
                toggleMobileMenu
            );
        }


        /* =================================================
           LOAD MARKETS
        ================================================= */

        loadMarkets();
    }


    /* =====================================================
       START
    ====================================================== */

    if (
        document.readyState ===
        "loading"
    ) {

        document.addEventListener(
            "DOMContentLoaded",
            init
        );

    } else {

        init();
    }

})();