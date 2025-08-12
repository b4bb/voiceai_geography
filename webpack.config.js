const path = require('path');
const CopyPlugin = require('copy-webpack-plugin');

module.exports = {
    entry: './src/frontend/app.js',
    output: {
        filename: 'static/bundle.js',
        path: path.resolve(__dirname, 'dist'),
        publicPath: '/'
    },
    devServer: {
        static: {
            directory: path.join(__dirname, 'dist'),
        },
        port: 8080,
        proxy: {
            '/api': 'http://localhost:3000'
        },
        hot: true
    },
    module: {
        rules: [
            {
                test: /\.js$/,
                exclude: /node_modules/,
                use: {
                    loader: 'babel-loader',
                    options: {
                        presets: ['@babel/preset-env']
                    }
                }
            }
        ]
    },
    plugins: [
        new CopyPlugin({
            patterns: [
                { from: 'src/frontend/dist/index.html', to: 'index.html' },
                { from: 'src/frontend/dist/styles.css', to: 'static/styles.css' }
            ],
        }),
    ]
};
