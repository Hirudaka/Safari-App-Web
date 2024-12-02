# In to the Jungle - Safari Web App 🐆🐘

### Installation

```bash
$ npm install
```

or

```bash
$ yarn install
```

### Basic usage

```bash
# dev server with hot reload at http://localhost:3000
$ npm start
```

or

```bash
# dev server with hot reload at http://localhost:3000
$ yarn start
```

Navigate to [http://localhost:3000](http://localhost:3000). The app will automatically reload if you change any of the source files.

#### Build

Run `build` to build the project. The build artifacts will be stored in the `build/` directory.

```bash
# build for production with minification
$ npm run build
```

or

```bash
# build for production with minification
$ yarn build
```

├── public/ # static files
│ ├── favicon.ico
│ └── manifest.json
│
├── src/ # project root
│ ├── assets/ # images, icons, etc.
│ ├── components/ # common components - header, footer, sidebar, etc.
│ ├── layouts/ # layout containers
│ ├── scss/ # scss styles
│ ├── views/ # application views
│ ├── \_nav.js # sidebar navigation config
│ ├── App.js
│ ├── index.js
│ ├── routes.js # routes config
│ └── store.js # template state example
│
├── index.html # html template
├── ...
├── package.json
├── ...
└── vite.config.mjs # vite config


# Architecture Diagram 
![WhatsApp Image 2024-11-30 at 6 35 48 PM](https://github.com/user-attachments/assets/af32a280-621a-4dd7-8824-8471ef5d0821)

## About Project

- Sri Lanka offers incredible safari experiences, but several challenges can affect the enjoyment and safety of these adventures. 

- Key issues include travelers' lack of wildlife knowledge, drivers exceeding speed limits and causing traffic jams, confusion about route coverage, and insufficient emergency communication due to poor cell phone coverage. 

- Our innovative solution leverages AI/ML, image processing, and location tracking to address these problems, enhancing educational experiences, providing offline emergency features, improving safety, and offering a more immersive exploration of Sri Lanka's natural wonders.

### Dependecies
```bash
 "dependencies": {
    "@coreui/chartjs": "^4.0.0",
    "@coreui/coreui": "^5.2.0",
    "@coreui/icons": "^3.0.1",
    "@coreui/icons-react": "^2.3.0",
    "@coreui/react": "^5.4.1",
    "@coreui/react-chartjs": "^3.0.0",
    "@coreui/utils": "^2.0.2",
    "@popperjs/core": "^2.11.8",
    "chart.js": "^4.4.6",
    "classnames": "^2.5.1",
    "core-js": "^3.39.0",
    "leaflet": "^1.9.4",
    "leaflet-routing-machine": "^3.2.12",
    "prop-types": "^15.8.1",
    "react": "^18.3.1",
    "react-datepicker": "^7.5.0",
    "react-dom": "^18.3.1",
    "react-leaflet": "^4.2.1",
    "react-redux": "^9.1.2",
    "react-router-dom": "^6.28.0",
    "redux": "5.0.1",
    "simplebar-react": "^3.2.6"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.3.3",
    "autoprefixer": "^10.4.20",
    "eslint": "^8.57.0",
    "eslint-config-prettier": "^9.1.0",
    "eslint-plugin-prettier": "^5.2.1",
    "eslint-plugin-react": "^7.37.2",
    "eslint-plugin-react-hooks": "^4.6.2",
    "postcss": "^8.4.49",
    "prettier": "3.3.3",
    "sass": "^1.81.0",
    "vite": "^5.4.11"
  }
```







