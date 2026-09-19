

(function(){

    const fd = window.farmerData || {};
    const dbCrops = window.myCrops || []; 

    const state = {
        farmer:{
            name:    fd.name    || "Farmer",
            village: fd.village || "Location",
            phone:   fd.phone   || "",
            crops:   fd.crops   || "Not set",
            since:   fd.since   || "2024",
            land:    fd.land    || "Not set"
        },

        // Use the database crops here, not hardcoded data
        crops: dbCrops.map(c => ({
            id: c.id,
            name: c.crop_name,
            qty: c.quantity,
            unit: "KG",
            grade: c.grade,
            price: parseFloat(c.price),
            status: c.status
        })),

        // The rest remains hardcoded for now
        // We will replace these later with Flask APIs.
        prices:[
            {
                crop:"Tomato",
                market:"Junagadh Mandi",
                price:25,
                unit:"KG",
                trend:"up",
                change:"+4.2%"
            },
            {
                crop:"Wheat",
                market:"Rajkot Mandi",
                price:2450,
                unit:"Quintal",
                trend:"up",
                change:"+2.1%"
            },
            {
                crop:"Onion",
                market:"Junagadh Mandi",
                price:21,
                unit:"KG",
                trend:"down",
                change:"-1.4%"
            },
            {
                crop:"Cotton",
                market:"Amreli Mandi",
                price:7200,
                unit:"Quintal",
                trend:"up",
                change:"+3.5%"
            },
            {
                crop:"Cumin",
                market:"Unjha Mandi",
                price:28500,
                unit:"Quintal",
                trend:"down",
                change:"-1.1%"
            },
            {
                crop:"Castor",
                market:"Gondal Mandi",
                price:6350,
                unit:"Quintal",
                trend:"up",
                change:"+0.9%"
            }
        ],

        requests:[
            {
                id:1,
                buyer:"ABC Foods",
                crop:"Tomato",
                qty:"100 KG",
                when:"2 hours ago",
                price:"₹25/KG",
                status:"pending"
            },
            {
                id:2,
                buyer:"Gujarat AgroMart",
                crop:"Wheat",
                qty:"5 Quintal",
                when:"Yesterday",
                price:"₹2,450/Q",
                status:"pending"
            },
            {
                id:3,
                buyer:"Saurashtra Exports",
                crop:"Onion",
                qty:"150 KG",
                when:"3 days ago",
                price:"₹21/KG",
                status:"accepted"
            }
        ],

        buyers:[
            {
                name:"ABC Foods",
                loc:"Junagadh",
                deals:"Tomato, Onion",
                rating:"4.6"
            },
            {
                name:"Gujarat AgroMart",
                loc:"Rajkot",
                deals:"Wheat, Cotton",
                rating:"4.3"
            },
            {
                name:"Saurashtra Exports",
                loc:"Amreli",
                deals:"Onion, Cumin",
                rating:"4.8"
            },
            {
                name:"Kathiyawadi Mandi Traders",
                loc:"Gondal",
                deals:"Castor, Wheat",
                rating:"4.1"
            }
        ],

        orders:[
            {
                id:"ORD-2041",
                crop:"Onion",
                buyer:"Saurashtra Exports",
                qty:"150 KG",
                amount:"₹3,150",
                status:"Delivered",
                date:"10 Sep 2026"
            },
            {
                id:"ORD-2038",
                crop:"Wheat",
                buyer:"Gujarat AgroMart",
                qty:"5 Quintal",
                amount:"₹12,250",
                status:"In transit",
                date:"08 Sep 2026"
            },
            {
                id:"ORD-2030",
                crop:"Tomato",
                buyer:"ABC Foods",
                qty:"80 KG",
                amount:"₹2,000",
                status:"Delivered",
                date:"29 Aug 2026"
            }
        ],

        priceFilter:"All"
    };


    /* ---------- NAVIGATION CONFIG ---------- */

    const nav = {

        dashboard:{
            label:"Dashboard",
            view:"dashboard"
        },

        "my-crops":{
            label:"My Crops",
            view:"my-crops"
        },

        "market-prices":{
            label:"Market Prices",
            view:"market-prices"
        },

        buyers:{
            label:"Buyers",
            view:"buyers"
        },

        orders:{
            label:"Orders",
            view:"orders"
        },

        profile:{
            label:"Profile",
            view:"profile"
        }

    };


    let activeGroup = "dashboard";
    let activeView = "dashboard";


    const viewToGroup = {

        "dashboard":"dashboard",

        "my-crops":"my-crops",

        "market-prices":"market-prices",

        "buyers":"buyers",

        "buyer-requests":"buyers",

        "orders":"orders",

        "profile":"profile",

        "edit-profile":"profile"

    };


    /* ---------- SIDEBAR BUILD ---------- */

    const navList =
        document.getElementById('navList');


    Object.keys(nav).forEach(key => {

        const g = nav[key];

        const li =
            document.createElement('li');

        const btn =
            document.createElement('button');

        btn.className =
            'nav-btn'
            + (
                key === activeGroup
                    ? ' active'
                    : ''
            );

        btn.textContent =
            g.label;


        btn.addEventListener(
            'click',
            () => {

                activeGroup = key;

                goTo(g.view);

                renderNav();

            }
        );


        li.appendChild(btn);

        navList.appendChild(li);

    });


    function renderNav(){

        document
            .querySelectorAll('.nav-btn')
            .forEach((b, i) => {

                const key =
                    Object.keys(nav)[i];

                b.classList.toggle(
                    'active',
                    key === activeGroup
                );

            });

    }


    function goTo(id){

        activeView = id;

        document
            .querySelectorAll('.view')
            .forEach(v =>
                v.classList.remove('active')
            );


        const viewEl =
            document.getElementById(
                'view-' + id
            );


        if(viewEl){

            viewEl.classList.add('active');

        }


        window.scrollTo({
            top:0,
            behavior:'smooth'
        });


        renderNav();

    }


    /* ---------- DATA-NAV BINDING ---------- */

    document
        .querySelectorAll('[data-nav]')
        .forEach(el => {

            el.addEventListener(
                'click',
                () => {

                    const t =
                        el.getAttribute(
                            'data-nav'
                        );

                    activeGroup =
                        viewToGroup[t] || t;

                    goTo(t);

                }
            );

        });


    /* ---------- TOAST ---------- */

    function toast(msg){

        const t =
            document.getElementById('toast');

        t.textContent =
            msg;

        t.classList.add('show');

        clearTimeout(t._tm);

        t._tm =
            setTimeout(
                () =>
                    t.classList.remove('show'),
                2200
            );

    }


    function unitLabel(u){

        return u === 'KG'
            ? 'KG'
            : u;

    }


    /* ---------- DASHBOARD ---------- */

    function renderDashboard(){

        const f =
            state.farmer;


        const initials =
            f.name
                .split(' ')
                .map(w => w[0])
                .slice(0,2)
                .join('');


        document.getElementById('topAv')
            .textContent =
                initials[0] || 'F';


        document.getElementById('topName')
            .textContent =
                f.name;


        document.getElementById('logoInit')
            .textContent =
                "M";


        document.getElementById('greeting')
            .textContent =
                `Good Morning, ${
                    f.name.split(' ')[0]
                }!`;


        const totalCrops =
            state.crops.length;


        const activeListings =
            state.crops.filter(
                c => c.status === 'Available'
            ).length;


        // Orders and requests are hardcoded
        const pendingOrders =
            state.orders.filter(
                o => o.status === 'In transit'
            ).length
            +
            state.requests.filter(
                r => r.status === 'pending'
            ).length;


        const totalSales =
            state.orders.reduce(
                (s, o) =>
                    s +
                    Number(
                        o.amount.replace(
                            /[₹,]/g,
                            ''
                        )
                    ),
                0
            );


        document.getElementById(
            'statGrid'
        ).innerHTML = `

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
                    Need your attention
                </div>
            </div>


            <div class="stat-card">
                <div class="stat-label">
                    Total Sales
                </div>

                <div class="stat-value">
                    ₹${totalSales.toLocaleString('en-IN')}
                </div>

                <div class="stat-note">
                    This month
                </div>
            </div>

        `;


        document.getElementById(
            'dashCropList'
        ).innerHTML =

            state.crops
                .slice(0,3)
                .map(c => `

                    <div class="crop-row">

                        <div>

                            <div class="crop-name">
                                ${c.name}
                            </div>

                            <div class="crop-meta">
                                ${c.qty}
                                ${unitLabel(c.unit)}
                                ·
                                ${c.grade}
                            </div>

                        </div>


                        <div
                            style="text-align:right;"
                        >

                            <div class="crop-price">
                                ₹${c.price}/${
                                    c.unit === 'KG'
                                        ? 'KG'
                                        : 'Q'
                                }
                            </div>

                            <span
                                class="
                                    pill
                                    ${
                                        c.status === 'Available'
                                            ? 'pill-avail'
                                            :
                                        c.status === 'Pending'
                                            ? 'pill-pending'
                                            :
                                            'pill-sold'
                                    }
                                "
                            >
                                ${c.status}
                            </span>

                        </div>

                    </div>

                `)
                .join('')

            ||

            `<div class="empty">
                No crops listed yet.
            </div>`;


        document.getElementById(
            'dashPriceList'
        ).innerHTML =

            state.prices
                .slice(0,4)
                .map(p => `

                    <div class="price-row">

                        <div class="price-crop">
                            ${p.crop}
                        </div>

                        <div class="price-right">

                            <div class="price-val">
                                ₹${p.price.toLocaleString('en-IN')}/${
                                    p.unit === 'KG'
                                        ? 'KG'
                                        : 'Q'
                                }
                            </div>

                            <div
                                class="${
                                    p.trend === 'up'
                                        ? 'change-up'
                                        : 'change-down'
                                }"
                            >
                                ${
                                    p.trend === 'up'
                                        ? '▲'
                                        : '▼'
                                }
                                ${p.change}
                            </div>

                        </div>

                    </div>

                `)
                .join('');


        document.getElementById(
            'dashRequests'
        ).innerHTML =
            renderReqList(
                state.requests.slice(0,3)
            );


        bindReqButtons();

    }


    function renderReqList(list){

        if (!list.length){

            return `
                <div class="empty">
                    No buyer requests yet.
                </div>
            `;

        }


        return list.map(r => {

            const initials =
                r.buyer
                    .split(' ')
                    .map(w => w[0])
                    .slice(0,2)
                    .join('');


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
                                ${r.buyer}
                            </div>

                            <div class="req-meta">
                                ${r.crop}
                                ·
                                ${r.qty}
                                ·
                                ${r.when}
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
                            ${r.price}
                        </span>


                        ${
                            r.status === 'pending'

                                ? `

                                    <button
                                        class="btn btn-primary btn-sm"
                                        data-acc="${r.id}"
                                    >
                                        Accept
                                    </button>

                                    <button
                                        class="btn btn-outline btn-sm"
                                        data-dec="${r.id}"
                                    >
                                        Decline
                                    </button>

                                `

                                :

                                `

                                    <span
                                        class="
                                            pill
                                            ${
                                                r.status === 'accepted'
                                                    ? 'pill-avail'
                                                    : 'pill-sold'
                                            }
                                        "
                                    >
                                        ${r.status}
                                    </span>

                                `
                        }

                    </div>

                </div>

            `;

        }).join('');

    }


    function bindReqButtons(){

        document
            .querySelectorAll('[data-acc]')
            .forEach(b =>

                b.addEventListener(
                    'click',
                    () => {

                        const r =
                            state.requests.find(
                                x =>
                                    x.id ==
                                    b.getAttribute(
                                        'data-acc'
                                    )
                            );


                        if(r)
                            r.status =
                                'accepted';


                        toast(
                            `Accepted request from ${r.buyer}`
                        );


                        renderAll();

                    }
                )

            );


        document
            .querySelectorAll('[data-dec]')
            .forEach(b =>

                b.addEventListener(
                    'click',
                    () => {

                        const r =
                            state.requests.find(
                                x =>
                                    x.id ==
                                    b.getAttribute(
                                        'data-dec'
                                    )
                            );


                        if(r)
                            r.status =
                                'declined';


                        toast(
                            `Declined request from ${r.buyer}`
                        );


                        renderAll();

                    }
                )

            );

    }


    /* ---------- CROPS ---------- */

    function renderCrops(
        filter = ""
    ){

        const list =
            state.crops.filter(
                c =>
                    c.name
                        .toLowerCase()
                        .includes(
                            filter.toLowerCase()
                        )
            );


        const grid =
            document.getElementById(
                'cropGrid'
            );


        if (!list.length){

            grid.innerHTML = `
                <div class="empty">
                    No crops match "${filter}".
                </div>
            `;

            return;

        }


        grid.innerHTML =
            list.map(c => `

                <div class="crop-tile">

                    <div class="ct-top">

                        <span
                            class="crop-badge"
                        >
                            ${c.name
                                .charAt(0)
                                .toUpperCase()}
                        </span>

                        <span
                            class="
                                pill
                                ${
                                    c.status === 'Available'
                                        ? 'pill-avail'
                                        :
                                    c.status === 'Pending'
                                        ? 'pill-pending'
                                        :
                                        'pill-sold'
                                }
                            "
                        >
                            ${c.status}
                        </span>

                    </div>


                    <div class="ct-name">
                        ${c.name}
                    </div>


                    <div class="ct-row">
                        <span>Quantity</span>
                        <span>
                            ${c.qty}
                            ${unitLabel(c.unit)}
                        </span>
                    </div>


                    <div class="ct-row">
                        <span>Grade</span>
                        <span>
                            ${c.grade}
                        </span>
                    </div>


                    <div class="ct-row">
                        <span>Price</span>
                        <span>
                            ₹${c.price}/${
                                c.unit === 'KG'
                                    ? 'KG'
                                    : 'Q'
                            }
                        </span>
                    </div>


                    <div class="ct-actions">

                        <!-- Disabled until backend support exists -->

                        <button
                            class="btn btn-outline btn-sm"
                            disabled
                        >
                            Edit
                        </button>

                        <button
                            class="btn btn-danger btn-sm"
                            disabled
                        >
                            Delete
                        </button>

                    </div>

                </div>

            `)
            .join('');

    }


    document
        .getElementById(
            'cropSearch'
        )
        .addEventListener(
            'input',
            e =>
                renderCrops(
                    e.target.value
                )
        );


    document
        .getElementById(
            'openAddCrop'
        )
        .addEventListener(
            'click',
            () => {

                document
                    .getElementById(
                        'cropOverlay'
                    )
                    .classList.add(
                        'active'
                    );

            }
        );


    document
        .getElementById(
            'openAddCrop2'
        )
        .addEventListener(
            'click',
            () => {

                document
                    .getElementById(
                        'cropOverlay'
                    )
                    .classList.add(
                        'active'
                    );

            }
        );


    document
        .getElementById(
            'cancelCrop'
        )
        .addEventListener(
            'click',
            () =>
                document
                    .getElementById(
                        'cropOverlay'
                    )
                    .classList.remove(
                        'active'
                    )
        );


    document
        .getElementById(
            'cropOverlay'
        )
        .addEventListener(
            'click',
            e => {

                if (
                    e.target.id ===
                    'cropOverlay'
                ){

                    e.currentTarget
                        .classList.remove(
                            'active'
                        );

                }

            }
        );


    /* ---------- PRICES ---------- */

    function renderPrices(){

        const set = [
            "All",
            ...new Set(
                state.prices.map(
                    p => p.crop
                )
            )
        ];


        document.getElementById(
            'priceChips'
        ).innerHTML =

            set.map(c =>

                `
                    <button
                        class="
                            chip
                            ${
                                state.priceFilter === c
                                    ? 'active'
                                    : ''
                            }
                        "
                        data-chip="${c}"
                    >
                        ${c}
                    </button>
                `

            ).join('');


        document
            .querySelectorAll(
                '[data-chip]'
            )
            .forEach(
                b =>

                    b.addEventListener(
                        'click',
                        () => {

                            state.priceFilter =
                                b.getAttribute(
                                    'data-chip'
                                );

                            renderPrices();

                        }
                    )

            );


        const list =
            state.priceFilter === "All"

                ? state.prices

                : state.prices.filter(
                    p =>
                        p.crop ===
                        state.priceFilter
                );


        document.getElementById(
            'fullPrices'
        ).innerHTML = `

            <tr>
                <th>Crop</th>
                <th>Mandi</th>
                <th>Price</th>
                <th>Change</th>
            </tr>

            ${
                list.map(p => `

                    <tr>

                        <td>
                            ${p.crop}
                        </td>

                        <td>
                            ${p.market}
                        </td>

                        <td>
                            ₹${p.price.toLocaleString('en-IN')}/${
                                p.unit === 'KG'
                                    ? 'KG'
                                    : 'Q'
                            }
                        </td>

                        <td
                            class="${
                                p.trend === 'up'
                                    ? 'change-up'
                                    : 'change-down'
                            }"
                        >
                            ${
                                p.trend === 'up'
                                    ? '▲'
                                    : '▼'
                            }
                            ${p.change}
                        </td>

                    </tr>

                `).join('')
            }

        `;

    }


    /* ---------- BUYERS ---------- */

    function renderBuyers(){

        document.getElementById(
            'buyerGrid'
        ).innerHTML =

            state.buyers.map(b => `

                <div class="crop-tile">

                    <div class="ct-top">

                        <span
                            class="crop-badge"
                        >
                            ${b.name
                                .charAt(0)
                                .toUpperCase()}
                        </span>

                        <span
                            class="pill pill-pending"
                        >
                            ★ ${b.rating}
                        </span>

                    </div>


                    <div class="ct-name">
                        ${b.name}
                    </div>


                    <div class="ct-row">
                        <span>Location</span>
                        <span>${b.loc}</span>
                    </div>


                    <div class="ct-row">
                        <span>Buys</span>
                        <span>${b.deals}</span>
                    </div>


                    <div class="ct-actions">

                        <button
                            class="btn btn-primary btn-sm"
                            data-contact="${b.name}"
                        >
                            Contact
                        </button>

                    </div>

                </div>

            `).join('');


        document
            .querySelectorAll(
                '[data-contact]'
            )
            .forEach(
                b =>

                    b.addEventListener(
                        'click',
                        () =>
                            toast(
                                `Request sent to ${b.getAttribute('data-contact')}`
                            )
                    )

            );

    }


    function renderFullRequests(){

        document.getElementById(
            'fullRequests'
        ).innerHTML =
            renderReqList(
                state.requests
            );


        bindReqButtons();

    }


    /* ---------- ORDERS ---------- */

    function renderOrders(){

        document.getElementById(
            'ordersTbl'
        ).innerHTML = `

            <tr>
                <th>Order ID</th>
                <th>Crop</th>
                <th>Buyer</th>
                <th>Qty</th>
                <th>Amount</th>
                <th>Status</th>
                <th>Date</th>
            </tr>

            ${
                state.orders.map(o => `

                    <tr>

                        <td>
                            ${o.id}
                        </td>

                        <td>
                            ${o.crop}
                        </td>

                        <td>
                            ${o.buyer}
                        </td>

                        <td>
                            ${o.qty}
                        </td>

                        <td>
                            ${o.amount}
                        </td>

                        <td
                            class="${
                                o.status === 'Delivered'
                                    ? 'change-up'
                                    : ''
                            }"
                        >
                            ${o.status}
                        </td>

                        <td>
                            ${o.date}
                        </td>

                    </tr>

                `).join('')
            }

        `;

    }


    /* ---------- PROFILE ---------- */

    function renderProfile(){

        const f =
            state.farmer;


        const initials =
            f.name
                .split(' ')
                .map(
                    w => w[0]
                )
                .slice(0,2)
                .join('');


        document.getElementById(
            'profileView'
        ).innerHTML = `

            <div class="p-av">
                ${initials}
            </div>


            <div class="p-row">
                <span>Name</span>
                <span>${f.name}</span>
            </div>


            <div class="p-row">
                <span>
                    Village / District
                </span>

                <span>
                    ${f.village}
                </span>
            </div>


            <div class="p-row">
                <span>
                    Phone
                </span>

                <span>
                    ${f.phone}
                </span>
            </div>


            <div class="p-row">
                <span>
                    Crops grown
                </span>

                <span>
                    ${f.crops}
                </span>
            </div>


            <div class="p-row">
                <span>
                    Land size
                </span>

                <span>
                    ${f.land}
                </span>
            </div>


            <div class="p-row">
                <span>
                    Member since
                </span>

                <span>
                    ${f.since}
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


        document
            .querySelectorAll(
                '#profileView [data-nav]'
            )
            .forEach(
                el =>

                    el.addEventListener(
                        'click',
                        () => {

                            activeGroup =
                                'profile';

                            goTo(
                                'edit-profile'
                            );

                        }
                    )

            );

    }


    function renderEditProfile(){

        // Currently local-only.
        // Backend save logic was not implemented.

        const f =
            state.farmer;


        document.getElementById(
            'profileEdit'
        ).innerHTML = `

            <div class="field">

                <label>
                    Name
                </label>

                <input
                    id="pfName"
                    value="${f.name}"
                >

            </div>


            <div class="field">

                <label>
                    Village / District
                </label>

                <input
                    id="pfVillage"
                    value="${f.village}"
                >

            </div>


            <div class="field">

                <label>
                    Phone
                </label>

                <input
                    id="pfPhone"
                    value="${f.phone}"
                >

            </div>


            <div class="field">

                <label>
                    Crops grown
                </label>

                <input
                    id="pfCrops"
                    value="${f.crops}"
                >

            </div>


            <div class="field">

                <label>
                    Land size
                </label>

                <input
                    id="pfLand"
                    value="${f.land}"
                >

            </div>


            <div
                class="modal-actions"
                style="justify-content:flex-start;"
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


        document.getElementById(
            'pfSave'
        ).addEventListener(
            'click',
            () => {

                f.name =
                    document.getElementById(
                        'pfName'
                    ).value.trim()
                    || f.name;


                f.village =
                    document.getElementById(
                        'pfVillage'
                    ).value.trim()
                    || f.village;


                f.phone =
                    document.getElementById(
                        'pfPhone'
                    ).value.trim()
                    || f.phone;


                f.crops =
                    document.getElementById(
                        'pfCrops'
                    ).value.trim()
                    || f.crops;


                f.land =
                    document.getElementById(
                        'pfLand'
                    ).value.trim()
                    || f.land;


                toast(
                    "Profile updated (Local only)"
                );


                activeGroup =
                    'profile';


                goTo(
                    'profile'
                );


                renderAll();

            }
        );


        document.getElementById(
            'pfCancel'
        ).addEventListener(
            'click',
            () => {

                activeGroup =
                    'profile';

                goTo(
                    'profile'
                );

            }
        );

    }


    /* ---------- RENDER ALL ---------- */

    function renderAll(){

        renderDashboard();

        renderCrops(
            document.getElementById(
                'cropSearch'
            ).value || ""
        );

        renderPrices();

        renderBuyers();

        renderFullRequests();

        renderOrders();

        renderProfile();

        renderEditProfile();

    }


    document.getElementById(
        'menuToggle'
    ).addEventListener(
        'click',
        () => {

            document
                .querySelector(
                    '.sidebar'
                )
                .classList.toggle(
                    'collapsed'
                );

        }
    );


    /* ---------- INIT ---------- */

    renderAll();

    renderNav();

})();