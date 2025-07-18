// 自定義JavaScript功能

// 全域變數
let currentStrategy = null;
let currentParameters = {};
let isBacktestRunning = false;

// 頁面載入完成後初始化
$(document).ready(function() {
    initializeApp();
    
    // 全域事件監聽器
    setupGlobalEventListeners();
    
    // 初始化工具提示
    $('[data-toggle="tooltip"]').tooltip();
    
    // 初始化彈出視窗
    $('[data-toggle="popover"]').popover();
});

// 應用程式初始化
function initializeApp() {
    console.log('交易系統應用程式初始化中...');
    
    // 檢查系統狀態
    checkSystemStatus();
    
    // 載入策略列表
    loadStrategies();
    
    // 設定定時器
    setInterval(checkSystemStatus, 30000); // 每30秒檢查一次系統狀態
    
    console.log('應用程式初始化完成');
}

// 設定全域事件監聽器
function setupGlobalEventListeners() {
    // 檔案拖放上傳
    setupFileDragAndDrop();
    
    // 全域錯誤處理
    $(document).ajaxError(function(event, xhr, settings, error) {
        handleAjaxError(xhr, error);
    });
    
    // 全域成功處理
    $(document).ajaxSuccess(function(event, xhr, settings) {
        handleAjaxSuccess(xhr, settings);
    });
}

// 檢查系統狀態
function checkSystemStatus() {
    $.get('/api/system/status')
        .done(function(response) {
            if (response.status === 'success') {
                updateSystemStatusDisplay(response.status_info);
            }
        })
        .fail(function(xhr) {
            console.error('檢查系統狀態失敗:', xhr.responseText);
        });
}

// 更新系統狀態顯示
function updateSystemStatusDisplay(statusInfo) {
    // 更新狀態指示器
    $('.system-status').each(function() {
        const statusType = $(this).data('status-type');
        const statusElement = $(this);
        
        switch(statusType) {
            case 'api':
                statusElement.text(statusInfo.api_status === 'normal' ? '正常' : '異常')
                           .removeClass('badge-success badge-danger')
                           .addClass(statusInfo.api_status === 'normal' ? 'badge-success' : 'badge-danger');
                break;
            case 'database':
                statusElement.text(statusInfo.database_status === 'normal' ? '正常' : '異常')
                           .removeClass('badge-success badge-danger')
                           .addClass(statusInfo.database_status === 'normal' ? 'badge-success' : 'badge-danger');
                break;
            case 'auto-trading':
                statusElement.text(statusInfo.auto_trading_status === 'running' ? '執行中' : '停止')
                           .removeClass('badge-success badge-secondary')
                           .addClass(statusInfo.auto_trading_status === 'running' ? 'badge-success' : 'badge-secondary');
                break;
        }
    });
}

// 載入策略列表
function loadStrategies() {
    $.get('/api/strategies')
        .done(function(response) {
            if (response.status === 'success') {
                populateStrategySelect(response.strategies);
            }
        })
        .fail(function(xhr) {
            showError('載入策略列表失敗: ' + xhr.responseText);
        });
}

// 填充策略選擇下拉選單
function populateStrategySelect(strategies) {
    const select = $('#strategy-select');
    if (select.length === 0) return;
    
    select.empty().append('<option value="">請選擇策略</option>');
    
    strategies.forEach(function(strategy) {
        select.append(`<option value="${strategy.name}">${strategy.display_name}</option>`);
    });
    
    // 如果有預設策略，自動選擇
    if (strategies.length > 0) {
        select.val(strategies[0].name).trigger('change');
    }
}

// 載入策略參數
function loadStrategyParameters(strategyName) {
    if (!strategyName) {
        $('#strategy-parameters').empty();
        return;
    }
    
    $.get(`/api/strategy/${strategyName}/parameters`)
        .done(function(response) {
            if (response.status === 'success') {
                renderStrategyParameters(response.parameters);
            }
        })
        .fail(function(xhr) {
            showError('載入策略參數失敗: ' + xhr.responseText);
        });
}

// 渲染策略參數
function renderStrategyParameters(parameters) {
    const container = $('#strategy-parameters');
    container.empty();
    
    if (Object.keys(parameters).length === 0) {
        container.append('<p class="text-muted">此策略無需額外參數</p>');
        return;
    }
    
    const row = $('<div class="row"></div>');
    
    Object.keys(parameters).forEach(function(key) {
        const param = parameters[key];
        const col = $('<div class="col-md-6"></div>');
        const formGroup = $('<div class="form-group"></div>');
        
        const label = $(`<label for="param-${key}">${param.label || key}</label>`);
        let input;
        
        if (param.type === 'number') {
            input = $(`<input type="number" class="form-control" id="param-${key}" 
                              value="${param.default || ''}" 
                              min="${param.min || ''}" 
                              max="${param.max || ''}" 
                              step="${param.step || '1'}">`);
        } else if (param.type === 'select') {
            input = $('<select class="form-control"></select>');
            param.options.forEach(function(option) {
                input.append(`<option value="${option.value}" ${option.value === param.default ? 'selected' : ''}>${option.label}</option>`);
            });
        } else if (param.type === 'boolean') {
            input = $(`<div class="custom-control custom-switch">
                          <input type="checkbox" class="custom-control-input" id="param-${key}" ${param.default ? 'checked' : ''}>
                          <label class="custom-control-label" for="param-${key}">${param.label || key}</label>
                       </div>`);
        } else {
            input = $(`<input type="text" class="form-control" id="param-${key}" value="${param.default || ''}">`);
        }
        
        if (param.required) {
            input.attr('required', true);
        }
        
        if (param.description) {
            const helpText = $(`<small class="form-text text-muted">${param.description}</small>`);
            formGroup.append(label).append(input).append(helpText);
        } else {
            formGroup.append(label).append(input);
        }
        
        col.append(formGroup);
        row.append(col);
    });
    
    container.append(row);
}

// 收集策略參數
function collectStrategyParameters() {
    const parameters = {};
    
    $('#strategy-parameters input, #strategy-parameters select').each(function() {
        const id = $(this).attr('id');
        if (id && id.startsWith('param-')) {
            const key = id.replace('param-', '');
            const element = $(this);
            
            if (element.attr('type') === 'checkbox') {
                parameters[key] = element.is(':checked');
            } else {
                parameters[key] = element.val();
            }
        }
    });
    
    return parameters;
}

// 設定檔案拖放上傳
function setupFileDragAndDrop() {
    $('.file-upload-area').each(function() {
        const area = $(this);
        
        area.on('dragover', function(e) {
            e.preventDefault();
            area.addClass('dragover');
        });
        
        area.on('dragleave', function(e) {
            e.preventDefault();
            area.removeClass('dragover');
        });
        
        area.on('drop', function(e) {
            e.preventDefault();
            area.removeClass('dragover');
            
            const files = e.originalEvent.dataTransfer.files;
            if (files.length > 0) {
                handleFileUpload(files[0], area);
            }
        });
        
        area.on('click', function() {
            const input = area.find('input[type="file"]');
            if (input.length > 0) {
                input.click();
            }
        });
    });
}

// 處理檔案上傳
function handleFileUpload(file, uploadArea) {
    const allowedTypes = ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel'];
    
    if (!allowedTypes.includes(file.type)) {
        showError('只支援Excel檔案格式 (.xlsx, .xls)');
        return;
    }
    
    if (file.size > 50 * 1024 * 1024) { // 50MB限制
        showError('檔案大小不能超過50MB');
        return;
    }
    
    // 顯示上傳進度
    showUploadProgress(uploadArea);
    
    // 這裡可以實作實際的檔案上傳邏輯
    // 目前只是模擬上傳
    setTimeout(function() {
        hideUploadProgress(uploadArea);
        showSuccess('檔案上傳成功: ' + file.name);
        
        // 更新檔案名稱顯示
        uploadArea.find('.file-name').text(file.name);
        uploadArea.addClass('has-file');
    }, 2000);
}

// 顯示上傳進度
function showUploadProgress(uploadArea) {
    const progressHtml = `
        <div class="upload-progress">
            <div class="progress">
                <div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" style="width: 0%"></div>
            </div>
            <small class="text-muted">上傳中...</small>
        </div>
    `;
    
    uploadArea.find('.upload-progress').remove();
    uploadArea.append(progressHtml);
    
    // 模擬進度條動畫
    const progressBar = uploadArea.find('.progress-bar');
    let progress = 0;
    const interval = setInterval(function() {
        progress += Math.random() * 20;
        if (progress >= 100) {
            progress = 100;
            clearInterval(interval);
        }
        progressBar.css('width', progress + '%');
    }, 200);
}

// 隱藏上傳進度
function hideUploadProgress(uploadArea) {
    uploadArea.find('.upload-progress').remove();
}

// 執行回測
function executeBacktest() {
    if (isBacktestRunning) {
        showWarning('回測正在執行中，請稍候...');
        return;
    }
    
    const strategy = $('#strategy-select').val();
    if (!strategy) {
        showError('請選擇策略');
        return;
    }
    
    const parameters = collectStrategyParameters();
    const dataSource = $('#data-source').val();
    const stockSource = $('#stock-source').val();
    const startDate = $('#start-date').val();
    const endDate = $('#end-date').val();
    const initialCapital = parseFloat($('#initial-capital').val());
    
    if (!startDate || !endDate || !initialCapital) {
        showError('請填寫完整的回測參數');
        return;
    }
    
    // 建立表單資料
    const formData = new FormData();
    formData.append('strategy', strategy);
    formData.append('parameters', JSON.stringify(parameters));
    formData.append('data_source', dataSource);
    formData.append('stock_source', stockSource);
    formData.append('start_date', startDate);
    formData.append('end_date', endDate);
    formData.append('initial_capital', initialCapital);
    
    // 添加檔案
    const priceFile = $('#price-file')[0].files[0];
    const stockFile = $('#stock-file')[0].files[0];
    
    if (dataSource === 'excel' && priceFile) {
        formData.append('price_file', priceFile);
    }
    
    if (stockSource === 'excel' && stockFile) {
        formData.append('stock_file', stockFile);
    }
    
    // 顯示載入狀態
    isBacktestRunning = true;
    showBacktestProgress();
    
    // 發送請求
    $.ajax({
        url: '/api/backtest/execute',
        method: 'POST',
        data: formData,
        processData: false,
        contentType: false
    })
    .done(function(response) {
        if (response.status === 'success') {
            displayBacktestResults(response.results);
        }
    })
    .fail(function(xhr) {
        showError('執行回測失敗: ' + xhr.responseText);
    })
    .always(function() {
        isBacktestRunning = false;
        hideBacktestProgress();
    });
}

// 顯示回測進度
function showBacktestProgress() {
    const progressHtml = `
        <div class="backtest-progress">
            <div class="text-center">
                <div class="loading-spinner"></div>
                <p class="mt-2">回測執行中，請稍候...</p>
            </div>
        </div>
    `;
    
    $('#backtest-results').html(progressHtml);
}

// 隱藏回測進度
function hideBacktestProgress() {
    $('.backtest-progress').remove();
}

// 顯示回測結果
function displayBacktestResults(results) {
    const container = $('#backtest-results');
    container.empty();
    
    // 統計摘要
    const summaryHtml = `
        <div class="row mb-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-chart-pie"></i> 回測統計摘要</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-2">
                                <div class="stat-card">
                                    <div class="stat-title">總交易次數</div>
                                    <div class="stat-value">${results.total_trades}</div>
                                </div>
                            </div>
                            <div class="col-md-2">
                                <div class="stat-card">
                                    <div class="stat-title">勝率</div>
                                    <div class="stat-value">${(results.win_rate * 100).toFixed(2)}%</div>
                                </div>
                            </div>
                            <div class="col-md-2">
                                <div class="stat-card">
                                    <div class="stat-title">總報酬</div>
                                    <div class="stat-value ${results.total_profit_loss_rate >= 0 ? 'text-success' : 'text-danger'}">${(results.total_profit_loss_rate * 100).toFixed(2)}%</div>
                                </div>
                            </div>
                            <div class="col-md-2">
                                <div class="stat-card">
                                    <div class="stat-title">最大回撤</div>
                                    <div class="stat-value text-danger">${(results.max_drawdown_rate * 100).toFixed(2)}%</div>
                                </div>
                            </div>
                            <div class="col-md-2">
                                <div class="stat-card">
                                    <div class="stat-title">夏普比率</div>
                                    <div class="stat-value">${results.sharpe_ratio.toFixed(2)}</div>
                                </div>
                            </div>
                            <div class="col-md-2">
                                <div class="stat-card">
                                    <div class="stat-title">淨損益</div>
                                    <div class="stat-value ${results.total_profit_loss >= 0 ? 'text-success' : 'text-danger'}">${results.total_profit_loss.toLocaleString()}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    container.append(summaryHtml);
    
    // 交易記錄表格
    if (results.trade_records && results.trade_records.length > 0) {
        const tableHtml = `
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <h5><i class="fas fa-table"></i> 交易記錄</h5>
                            <div>
                                <button type="button" class="btn btn-success" onclick="exportBacktestResults('detailed')">
                                    <i class="fas fa-file-excel"></i> 匯出詳細記錄
                                </button>
                                <button type="button" class="btn btn-info" onclick="exportBacktestResults('basic')">
                                    <i class="fas fa-file-excel"></i> 匯出基本記錄
                                </button>
                            </div>
                        </div>
                        <div class="card-body">
                            <div class="table-responsive">
                                <table class="table table-striped table-hover">
                                    <thead class="thead-dark">
                                        <tr>
                                            <th>進場日期</th>
                                            <th>出場日期</th>
                                            <th>股票代碼</th>
                                            <th>方向</th>
                                            <th>進場價格</th>
                                            <th>出場價格</th>
                                            <th>股數</th>
                                            <th>損益</th>
                                            <th>損益率</th>
                                            <th>淨損益</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        ${results.trade_records.map(trade => `
                                            <tr>
                                                <td>${formatDate(trade.entry_date)}</td>
                                                <td>${formatDate(trade.exit_date)}</td>
                                                <td>${trade.stock_id}</td>
                                                <td><span class="badge ${trade.trade_direction === 'buy' ? 'badge-success' : 'badge-danger'}">${trade.trade_direction === 'buy' ? '買入' : '賣出'}</span></td>
                                                <td>${formatPrice(trade.entry_price)}</td>
                                                <td>${formatPrice(trade.exit_price)}</td>
                                                <td>${trade.shares.toLocaleString()}</td>
                                                <td class="${trade.profit_loss >= 0 ? 'text-success' : 'text-danger'}">${formatMoney(trade.profit_loss)}</td>
                                                <td class="${trade.profit_loss_rate >= 0 ? 'text-success' : 'text-danger'}">${formatPercentage(trade.profit_loss_rate)}</td>
                                                <td class="${trade.net_profit_loss >= 0 ? 'text-success' : 'text-danger'} font-weight-bold">${formatMoney(trade.net_profit_loss)}</td>
                                            </tr>
                                        `).join('')}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        container.append(tableHtml);
    }
    
    // 圖表
    if (results.charts && results.charts.length > 0) {
        const chartsHtml = `
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5><i class="fas fa-chart-line"></i> 績效圖表</h5>
                        </div>
                        <div class="card-body">
                            <div id="charts-container">
                                <!-- 圖表將在這裡動態載入 -->
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        container.append(chartsHtml);
        
        // 載入圖表
        loadCharts(results);
    }
    
    // 添加動畫效果
    container.addClass('fade-in');
}

// 載入圖表
function loadCharts(results) {
    // 這裡可以整合Chart.js或其他圖表庫
    // 目前只是顯示佔位符
    const container = $('#charts-container');
    
    if (results.equity_curve && results.equity_curve.length > 0) {
        const chartHtml = `
            <div class="chart-container">
                <h6>權益曲線</h6>
                <div class="text-center text-muted">
                    <i class="fas fa-chart-line fa-3x mb-3"></i>
                    <p>圖表功能開發中...</p>
                </div>
            </div>
        `;
        container.append(chartHtml);
    }
}

// 匯出回測結果
function exportBacktestResults(exportType) {
    const results = window.currentBacktestResults;
    if (!results) {
        showError('沒有可匯出的回測結果');
        return;
    }
    
    const exportData = {
        results: results,
        export_type: exportType
    };
    
    $.ajax({
        url: '/api/backtest/export-excel',
        method: 'POST',
        data: JSON.stringify(exportData),
        contentType: 'application/json'
    })
    .done(function(response) {
        // 下載檔案
        const blob = new Blob([response], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `backtest_results_${new Date().toISOString().split('T')[0]}.xlsx`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        showSuccess('回測結果匯出成功');
    })
    .fail(function(xhr) {
        showError('匯出失敗: ' + xhr.responseText);
    });
}

// 工具函數
function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('zh-TW');
}

function formatPrice(price) {
    return price ? price.toFixed(2) : '-';
}

function formatMoney(amount) {
    if (amount === null || amount === undefined) return '-';
    return amount.toLocaleString('zh-TW', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    });
}

function formatPercentage(value) {
    if (value === null || value === undefined) return '-';
    return (value * 100).toFixed(2) + '%';
}

// 訊息顯示函數
function showSuccess(message) {
    showAlert('success', message);
}

function showError(message) {
    showAlert('danger', message);
}

function showWarning(message) {
    showAlert('warning', message);
}

function showInfo(message) {
    showAlert('info', message);
}

function showAlert(type, message) {
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="close" data-dismiss="alert">
                <span>&times;</span>
            </button>
        </div>
    `;
    
    $('.container-fluid').prepend(alertHtml);
    
    // 自動移除警告
    setTimeout(function() {
        $('.alert').alert('close');
    }, 5000);
}

// AJAX錯誤處理
function handleAjaxError(xhr, error) {
    console.error('AJAX錯誤:', error);
    
    if (xhr.status === 401) {
        showError('請先登入系統');
    } else if (xhr.status === 403) {
        showError('權限不足');
    } else if (xhr.status === 404) {
        showError('請求的資源不存在');
    } else if (xhr.status === 500) {
        showError('伺服器內部錯誤');
    } else {
        showError('請求失敗: ' + error);
    }
}

// AJAX成功處理
function handleAjaxSuccess(xhr, settings) {
    // 可以在這裡添加全域的成功處理邏輯
    console.log('AJAX請求成功:', settings.url);
}

// 確認對話框
function showConfirmDialog(message, callback) {
    const modalHtml = `
        <div class="modal fade" id="confirmModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">確認操作</h5>
                        <button type="button" class="close" data-dismiss="modal">
                            <span>&times;</span>
                        </button>
                    </div>
                    <div class="modal-body">
                        <p>${message}</p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-dismiss="modal">取消</button>
                        <button type="button" class="btn btn-primary" id="confirm-btn">確認</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // 移除現有的確認對話框
    $('#confirmModal').remove();
    
    // 添加新的確認對話框
    $('body').append(modalHtml);
    
    // 設定確認按鈕事件
    $('#confirm-btn').click(function() {
        $('#confirmModal').modal('hide');
        if (callback) callback();
    });
    
    // 顯示對話框
    $('#confirmModal').modal('show');
    
    // 對話框關閉後移除
    $('#confirmModal').on('hidden.bs.modal', function() {
        $(this).remove();
    });
}

// 全域函數，供HTML直接調用
window.executeBacktest = executeBacktest;
window.exportBacktestResults = exportBacktestResults;
window.showConfirmDialog = showConfirmDialog; 