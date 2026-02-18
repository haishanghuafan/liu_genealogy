/**
 * 刘氏乾正公族谱 - ECharts家族树可视化
 */

// 关系类型中文映射
const RELATION_TYPE_MAP = {
    'marriage': '正室',
    'concubine': '妾室',
    'adopted': '继配',
    'first': '一房',
    'second': '二房',
    'third': '三房',
    'fourth': '四房',
    'fifth': '五房'
};

/**
 * 初始化家族树
 * @param {string} containerId - 容器ID
 * @param {number} personId - 人物ID
 */
function initFamilyTree(containerId, personId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const chart = echarts.init(container, null, {
        renderer: 'canvas',
        useDirtyRect: true
    });

    loadFamilyTreeData(chart, personId);

    window.addEventListener('resize', () => {
        chart.resize();
    });

    return chart;
}

/**
 * 加载家族树数据
 * @param {Object} chart - ECharts实例
 * @param {number} personId - 人物ID
 */
async function loadFamilyTreeData(chart, personId) {
    try {
        const response = await fetch(`/person/${personId}/family-tree/`);
        const data = await response.json();
        
        const treeData = transformToEChartsTree(data.tree);
        
        renderFamilyTree(chart, treeData, data.person);
        
    } catch (error) {
        console.error('加载家族树数据失败:', error);
    }
}

/**
 * 转换数据为ECharts树格式
 * @param {Object} node - 原始节点
 * @returns {Object} ECharts树节点
 */
function transformToEChartsTree(node) {
    const isFemale = node.gender === 'F';
    const isSpouse = !!node.relation_type;
    
    const echartsNode = {
        name: node.name,
        id: node.id,
        value: [node.generation],
        gender: node.gender,
        isSpouse: isSpouse,
        relationType: node.relation_type || null,
        children: [],
        itemStyle: {
            color: isFemale ? '#C71585' : '#8B4513',
            borderColor: isFemale ? '#A0136B' : '#6B3410',
            borderWidth: 2
        },
        symbolSize: isSpouse ? 70 : 80
    };

    if (node.children && node.children.length > 0) {
        echartsNode.children = node.children.map(child => transformToEChartsTree(child));
    }

    return echartsNode;
}

/**
 * 渲染家族树
 * @param {Object} chart - ECharts实例
 * @param {Object} treeData - 树数据
 * @param {Object} currentPerson - 当前人物信息
 */
function renderFamilyTree(chart, treeData, currentPerson) {
    const option = {
        title: {
            text: `家族关系图 - ${currentPerson.name}`,
            left: 'center',
            top: 10,
            textStyle: {
                fontSize: 16,
                color: '#333',
                fontFamily: 'Microsoft YaHei, SimSun, sans-serif',
                fontWeight: 'bold'
            }
        },
        tooltip: {
            trigger: 'item',
            backgroundColor: 'rgba(255,255,255,0.95)',
            borderColor: '#ddd',
            borderWidth: 1,
            textStyle: {
                color: '#333'
            },
            formatter: function(params) {
                const data = params.data;
                let html = `<div style="font-weight: bold; font-size: 14px; margin-bottom: 5px;">${data.name}</div>`;
                html += `<div style="font-size: 12px; color: #666;">世代: 第${data.value[0]}世</div>`;
                if (data.isSpouse && data.relationType) {
                    html += `<div style="font-size: 12px; color: #666;">关系: ${RELATION_TYPE_MAP[data.relationType] || '配偶'}</div>`;
                }
                html += `<div style="font-size: 11px; color: #999; margin-top: 8px; border-top: 1px solid #eee; padding-top: 5px;">点击查看详情</div>`;
                return html;
            }
        },
        toolbox: {
            show: true,
            right: 20,
            top: 20,
            feature: {
                dataZoom: {
                    yAxisIndex: 'none',
                    title: {
                        zoom: '区域缩放',
                        back: '区域缩放还原'
                    }
                },
                restore: {
                    title: '重置'
                },
                saveAsImage: {
                    title: '保存图片'
                }
            }
        },
        dataZoom: [
            {
                type: 'inside',
                start: 0,
                end: 100
            }
        ],
        series: [
            {
                type: 'tree',
                data: [treeData],
                top: '12%',
                left: '5%',
                bottom: '8%',
                right: '5%',
                symbol: 'circle',
                symbolSize: 80,
                edgeShape: 'curve',
                edgeForkPosition: '63%',
                initialTreeDepth: 4,
                layout: 'orthogonal',
                orient: 'TB',
                roam: true,
                expandAndCollapse: true,
                animationDuration: 550,
                animationDurationUpdate: 750,
                lineStyle: {
                    color: '#ccc',
                    width: 2,
                    curveness: 0.5
                },
                itemStyle: {
                    borderColor: '#fff',
                    borderWidth: 3
                },
                label: {
                    show: true,
                    position: 'inside',
                    verticalAlign: 'middle',
                    align: 'center',
                    color: '#fff',
                    fontSize: 13,
                    fontWeight: 'bold',
                    fontFamily: 'Microsoft YaHei, SimSun, sans-serif',
                    lineHeight: 16,
                    formatter: function(params) {
                        const data = params.data;
                        let text = data.name || '';
                        if (data.isSpouse && data.relationType) {
                            const relationType = RELATION_TYPE_MAP[data.relationType] || '配偶';
                            text += `\n(${relationType})`;
                        }
                        return text;
                    }
                },
                leaves: {
                    label: {
                        show: true,
                        position: 'inside',
                        verticalAlign: 'middle',
                        align: 'center',
                        color: '#fff',
                        fontSize: 13,
                        fontWeight: 'bold'
                    }
                },
                emphasis: {
                    focus: 'descendant',
                    itemStyle: {
                        shadowBlur: 20,
                        shadowColor: 'rgba(0,0,0,0.3)'
                    }
                }
            }
        ]
    };

    chart.setOption(option, true);

    chart.on('click', function(params) {
        if (params.data && params.data.id) {
            window.location.href = `/person/${params.data.id}/`;
        }
    });
}

/**
 * 初始化多视图家族树
 * @param {string} containerId - 容器ID
 * @param {number} personId - 人物ID
 * @param {string} layout - 布局类型
 */
function initMultiViewFamilyTree(containerId, personId, layout = 'horizontal') {
    const container = document.getElementById(containerId);
    if (!container) return;

    const chart = echarts.init(container);
    
    loadFamilyTreeData(chart, personId, layout);
    
    window.addEventListener('resize', () => chart.resize());
    
    return chart;
}

window.initFamilyTree = initFamilyTree;
window.initMultiViewFamilyTree = initMultiViewFamilyTree;
