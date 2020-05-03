module.exports = {
    extends: ['@atol/eslint-config-atol'],
    rules: {
        'react/jsx-fragments': 'off',
        'react/jsx-props-no-spreading': 'off',
        'react/prop-types': 'off',
    },
    "settings": {
        "import/resolver": {
          "node": {
            "paths": ["src"],
            "extensions": [".js", ".jsx", ".ts", ".tsx"]
          }
        }
      },
};
