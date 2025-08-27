(function($) {
    'use strict';
    
    // Store volunteer type data
    var volunteerTypeData = {};
    
    // Fetch volunteer type data when page loads
    $(document).ready(function() {
        // Get volunteer type data from API
        $.ajax({
            url: '/admin/signups/volunteerform/volunteer-types/',
            method: 'GET',
            success: function(data) {
                // Store volunteer type data
                data.forEach(function(type) {
                    volunteerTypeData[type.name] = type.description;
                });
            },
            error: function() {
                console.log('Could not fetch volunteer type data');
            }
        });
        
        // Handle volunteer type selection changes
        $('#id_volunteer_type').on('change', function() {
            var select = $(this);
            var titleField = $('#id_title');
            var descriptionField = $('#id_description');
            var selectedOption = select.find('option:selected');
            var selectedText = selectedOption.text();
            
            if (selectedText && selectedText !== '---------') {
                // Auto-populate title with the volunteer type name
                titleField.val(selectedText);
                
                // Auto-populate description from volunteer type data
                if (volunteerTypeData[selectedText]) {
                    descriptionField.val(volunteerTypeData[selectedText]);
                }
            }
        });
    });
    
})(django.jQuery);
