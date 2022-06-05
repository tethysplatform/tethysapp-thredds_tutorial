/*****************************************************************************
 * FILE:      Leaflet Map Module for THREDDS Tutorial
 * DATE:      13 December 2019
 * AUTHOR:    Nathan Swain
 * COPYRIGHT: (c) Aquaveo 2019
 * LICENSE:   BSD 2-Clause
 *****************************************************************************/

/*****************************************************************************
 *                      LIBRARY WRAPPER
 *****************************************************************************/

var LEAFLET_MAP = (function() {
    "use strict"; // And enable strict mode for this library

    /************************************************************************
    *                      MODULE LEVEL / GLOBAL VARIABLES
    *************************************************************************/
    var public_interface,    // Object returned by the module
        m_map,               // The Leaflet Map
        m_layer,             // The layer
        m_td_layer,          // The Time-Dimension layer
        m_layer_meta,        // Map of layer metadata indexed by variable
        m_curr_dataset,      // The current selected dataset
        m_curr_variable,     // The current selected variable/layer
        m_curr_style,        // The current selected style
        m_curr_wms_url;      // The current WMS url

    /************************************************************************
    *                    PRIVATE FUNCTION DECLARATIONS
    *************************************************************************/
    // Map Methods
    var init_map, update_layer;

    // Control Methods
    var init_controls, update_variable_control, update_style_control;

    // Legend Methods
    var update_legend, clear_legend;

    // Loader Methods
    var show_loader, hide_loader;

    /************************************************************************
    *                    PRIVATE FUNCTION IMPLEMENTATIONS
    *************************************************************************/
    // Map Methods
    init_map = function() {
        // Create Map
        m_map = L.map('leaflet-map', {
            zoom: 3,
            center: [0, 0],
            fullscreenControl: true,
            timeDimension: true,
            timeDimensionControl: true
        });

        // Add Basemap
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(m_map);
    };

    update_layer = function() {
        if (m_td_layer) {
            m_map.removeLayer(m_td_layer);
        }

        // Clear the legend
        clear_legend();

        // Layer
        m_layer = L.tileLayer.wms(m_curr_wms_url, {
            layers: m_curr_variable,
            format: 'image/png',
            transparent: true,
            colorscalerange: '250,350',  // Hard-coded color scale range won't work for all layers
            abovemaxcolor: "extend",
            belowmincolor: "extend",
            numcolorbands: 100,
            styles: m_curr_style
        });

        // Wrap WMS layer in Time Dimension Layer
        m_td_layer = L.timeDimension.layer.wms(m_layer, {
            updateTimeDimension: true
        });

        // Add events for loading
        m_layer.on('loading', function() {
            show_loader();
        });

        m_layer.on('load', function() {
            hide_loader();
        });

        // Add Time-Dimension-Wrapped WMS layer to the Map
        m_td_layer.addTo(m_map);

        // Update the legend graphic
        update_legend();
    };

    // Control Methods
    init_controls = function() {
        // Define what happens when the dataset select input changes
        $('#dataset').on('change', function() {
            let dataset_wms = $('#dataset').val();
            let dataset_wms_parts = dataset_wms.split(';');
            m_curr_dataset = dataset_wms_parts[0];
            m_curr_wms_url = dataset_wms_parts[1];

            // Update variable control with layers provided by the new WMS
            update_variable_control();
        });

        // Define what happens when the variable select input changes
        $('#variable').on('change', function() {
            m_curr_variable = $('#variable').val();

            // Update the styles
            update_style_control();

            // Zoom to the bounding box of the new layer
            let bbox = m_layer_meta[m_curr_variable].bbox;
            m_map.fitBounds(bbox);
        });

        // Define what happens when the style select input changes
        $('#style').on('change', function() {
            m_curr_style = $('#style').val();

            // Update the layer with the new styles
            update_layer();
        });

        $('#dataset').trigger('change');
    };

    // Query the current WMS for available layers and add them to the variable control
    update_variable_control = function() {
        // Show loader
        show_loader();

        // Use REST endpoint to get WMS layers
        fetch('./get-wms-layers/?' + new URLSearchParams({'wms_url': m_curr_wms_url}))
          .then((response) => response.json())
          .then((data) => {
            if (!data.success) {
                console.log('An unexpected error occurred!');
                return;
            }

            // Clear current variable select options
            $('#variable').select2().empty();

            // Save layer metadata
            m_layer_meta = data.layers;

            // Create new variable select options
            let first_option = true;
            for (var layer in data.layers) {
                if (first_option) {
                    m_curr_variable = layer;
                }

                let new_option = new Option(layer, layer, first_option, first_option);
                $('#variable').append(new_option);
                first_option = false;
            }

            // Trigger a change to refresh the select box
            $('#variable').trigger('change');

            // Hide the loader
            hide_loader();
          });
    };

    // Update the available style options on the style control
    update_style_control = function() {
        let first_option = true;
        for (var style in m_layer_meta[m_curr_variable].styles) {
            if (first_option) {
                m_curr_style = style;
            }

            let new_option = new Option(style, style, first_option, first_option);
            $('#style').append(new_option);
            first_option = false;
        }

        $('#style').trigger('change');
    };

    // Legend Methods
    update_legend = function() {
        let legend = m_layer_meta[m_curr_variable].styles[m_curr_style].legend;
        $('#legend').html('<li class="title">Legend<h1></li><img src="' + legend + '">');
    };

    clear_legend = function() {
        $('#legend').html('');
    };

    // Loader Methods
    show_loader = function() {
        $('#loader').addClass('show');
    };

    hide_loader = function() {
        $('#loader').removeClass('show');
    };

    /************************************************************************
    *                        DEFINE PUBLIC INTERFACE
    *************************************************************************/
    /*
     * Library object that contains public facing functions of the package.
     * This is the object that is returned by the library wrapper function.
     * See below.
     * NOTE: The functions in the public interface have access to the private
     * functions of the library because of JavaScript function scope.
     */
    public_interface = {};

    /************************************************************************
    *                  INITIALIZATION / CONSTRUCTOR
    *************************************************************************/

    // Initialization: jQuery function that gets called when
    // the DOM tree finishes loading
    $(function() {
        init_map();
        init_controls();
    });

    return public_interface;

}()); // End of package wrapper
