FROM node:20
WORKDIR /app
COPY package.json tsconfig.json next.config.js tailwind.config.ts postcss.config.js ./
COPY app ./app
COPY next-env.d.ts ./
COPY app/globals.css ./app/globals.css
RUN npm install
RUN npx tailwindcss -i ./app/globals.css -o ./public/styles.css --minify || true
CMD ["npm", "run", "dev", "--", "-H", "0.0.0.0"]
