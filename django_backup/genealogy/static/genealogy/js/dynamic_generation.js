(function($) {
    $(document).ready(function() {
        // 获取是否为外族配偶的复选框
        var outsiderCheckbox = $('#id_is_outsider');
        // 获取性别选择
        var genderSelect = $('#id_gender');
        // 获取世代选择的下拉菜单
        var generationSelect = $('#id_generation');
        
        // 监听复选框的变化事件
        outsiderCheckbox.on('change', function() {
            var isOutsider = $(this).is(':checked');
            
            // 发送AJAX请求获取对应的世代选项
            $.ajax({
                url: '/get_generations/',
                type: 'GET',
                data: {
                    'is_outsider': isOutsider
                },
                dataType: 'json',
                success: function(data) {
                    // 清空当前的选项
                    generationSelect.empty();
                    
                    // 添加新的选项
                    $.each(data.generations, function(index, generation) {
                        generationSelect.append($('<option>', {
                            value: generation.id,
                            text: generation.name
                        }));
                    });
                },
                error: function() {
                    console.error('获取世代选项失败');
                }
            });
            
            // 显示提示，告诉用户需要保存并重新加载页面
            alert('外族配偶状态变更后，配偶关系选项会自动调整，请保存当前更改并重新加载页面。');
        });
        
        // 监听性别变化事件
        genderSelect.on('change', function() {
            // 显示提示，告诉用户需要保存并重新加载页面
            alert('性别变更后，配偶关系选项会自动更新，请保存当前更改并重新加载页面。');
        });
    });
})(django.jQuery);