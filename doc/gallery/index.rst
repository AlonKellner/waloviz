Gallery
_______

.. raw:: html

    <script>
    function gallery_toggle(input) {
        backends = ['bokeh'];
        for (i in backends) {
            entries = $('.'+backends[i]+'-example').parent();
            if (backends[i] == input) {
                entries.show();
            } else {
                entries.attr('style','display: none !important')
            }
        }
    }
    </script>

    <ul class="tab">
    
        <li>
            <input id="tab1" checked="checked" type="radio" name="tab" onclick="gallery_toggle('Bokeh'.toLowerCase())" />
            <label for="tab1">Bokeh</label>
        </li>

    </ul>

.. toctree::
   :glob:
   :hidden:

   
   *

.. grid:: 2 2 4 5
    :gutter: 3
    :margin: 0


.. toctree::
   :glob:
   :hidden:


.. raw:: html

    <script>
        $(document).ready(function () {
            backends = [];
            for (var i=0; i<backends.length; i++){
                $('.'+backends[i]+'-example').parent().attr('style','display: none !important');
            }
        });
    </script>
