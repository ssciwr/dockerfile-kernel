"use strict";
(self["webpackChunkshell_extension"] = self["webpackChunkshell_extension"] || []).push([["lib_index_js"],{

/***/ "./lib/index.js":
/*!**********************!*\
  !*** ./lib/index.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   ButtonExtension: () => (/* binding */ ButtonExtension),
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _lumino_disposable__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @lumino/disposable */ "webpack/sharing/consume/default/@lumino/disposable");
/* harmony import */ var _lumino_disposable__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_lumino_disposable__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__);


/**
 * The plugin registration information.
 */
const plugin = {
    activate,
    id: 'toolbar-shell-button',
    autoStart: true,
};
/**
 * A notebook widget extension that adds a button to the toolbar.
 */
class ButtonExtension {
    constructor(init) {
        this.app = undefined;
        Object.assign(this, init);
    }
    /**
     * Create a new extension that shows button in the toolbar.
     * The button can be used to create a console instance for the notebook.
     *
     * @param panel Notebook panel
     * @returns Disposable on the added button
     */
    createNew(panel) {
        const createConsole = () => {
            var _a;
            (_a = this.app) === null || _a === void 0 ? void 0 : _a.commands.execute('notebook:create-console');
        };
        const button = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.ToolbarButton({
            className: 'create-console-button',
            label: 'Create Console',
            onClick: createConsole,
            tooltip: 'Create console for current notebook'
        });
        // 10 is the index in the standard toolbar to correctly place the button
        panel.toolbar.insertItem(10, 'createConsole', button);
        return new _lumino_disposable__WEBPACK_IMPORTED_MODULE_0__.DisposableDelegate(() => {
            button.dispose();
        });
    }
}
/**
 * Activate the extension.
 *
 * @param app Main application object
 */
function activate(app) {
    app.docRegistry.addWidgetExtension('Notebook', new ButtonExtension({ app: app }));
}
/**
 * Export the plugin as default.
 */
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (plugin);


/***/ })

}]);
//# sourceMappingURL=lib_index_js.6208d44c69ab5d8d0af3.js.map