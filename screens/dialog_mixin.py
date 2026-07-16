# screens/dialog_mixin.py
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRectangleFlatButton


class DialogMixin:
    """Барча экранлар учун умумий диалог методлари"""
    
    # ========== ОДДИЙ ХАБАРЛАР ==========
    def show_error(self, message):
        dialog = MDDialog(
            title="❌ Хатолик",
            text=str(message),
        )
        dialog.buttons = [MDRectangleFlatButton(
            text="OK",
            on_release=lambda x, dlg=dialog: dlg.dismiss()
        )]
        dialog.open()
    
    def show_success(self, message):
        dialog = MDDialog(
            title="✅ Муваффақият",
            text=str(message),
        )
        dialog.buttons = [MDRectangleFlatButton(
            text="OK",
            on_release=lambda x, dlg=dialog: dlg.dismiss()
        )]
        dialog.open()
    
    def show_warning(self, message):
        dialog = MDDialog(
            title="⚠️ Огоҳлантириш",
            text=str(message),
        )
        dialog.buttons = [MDRectangleFlatButton(
            text="OK",
            on_release=lambda x, dlg=dialog: dlg.dismiss()
        )]
        dialog.open()
    
    def show_info(self, message):
        dialog = MDDialog(
            title="ℹ️ Маълумот",
            text=str(message),
        )
        dialog.buttons = [MDRectangleFlatButton(
            text="OK",
            on_release=lambda x, dlg=dialog: dlg.dismiss()
        )]
        dialog.open()
    
    # ========== ТАСДИҚЛАШ ==========
    def show_confirm(self, message, on_yes=None, on_no=None,
                     title="Тасдиқлаш", yes_text="ҲА", no_text="БЕКОР"):
        dialog = MDDialog(
            title=title,
            text=str(message),
        )
        dialog.buttons = [
            MDRectangleFlatButton(
                text=no_text,
                on_release=lambda x, dlg=dialog: self._handle_confirm(dlg, False, on_no)
            ),
            MDRectangleFlatButton(
                text=yes_text,
                on_release=lambda x, dlg=dialog: self._handle_confirm(dlg, True, on_yes)
            )
        ]
        dialog.open()
    
    def _handle_confirm(self, dialog, confirmed, callback):
        dialog.dismiss()
        if callback:
            callback(confirmed)
    
    # ========== ТУГМАЛИ МУВАФФАҚИЯТ ==========
    def show_success_with_buttons(self, message, buttons_config):
        """
        Қўшимча тугмалар билан муваффақият диалоги.
        
        buttons_config = [
            {'text': '📄 ЧЕКНИ КЎРСАТ', 'callback': func1},
            {'text': '🖨️ ЧОП ЭТИШ', 'callback': func2},
            {'text': 'OK', 'dismiss': True}
        ]
        """
        dialog = MDDialog(
            title="✅ Муваффақият",
            text=str(message),
        )
        
        buttons = []
        for btn_config in buttons_config:
            text = btn_config.get('text', 'OK')
            callback = btn_config.get('callback', None)
            should_dismiss = btn_config.get('dismiss', False)
            
            if should_dismiss or (text == 'OK' and not callback):
                # Фақат диалогни ёпади
                btn = MDRectangleFlatButton(
                    text=text,
                    on_release=lambda x, dlg=dialog: dlg.dismiss()
                )
            else:
                # callback чақиради, диалог очиқ қолади
                btn = MDRectangleFlatButton(
                    text=text,
                    on_release=lambda x, cb=callback: cb()
                )
            buttons.append(btn)
        
        dialog.buttons = buttons
        dialog.open()
    
    # ========== МОСЛАШТИРИЛГАН ДИАЛОГ ==========
    def show_custom_dialog(self, title, content, buttons_config=None):
        """Мослаштирилган диалог"""
        dialog = MDDialog(
            title=title,
            type="custom",
            content_cls=content,
        )
        
        if buttons_config:
            buttons = []
            for btn_config in buttons_config:
                text = btn_config.get('text', 'OK')
                callback = btn_config.get('callback', None)
                should_dismiss = btn_config.get('dismiss', False)
                
                if should_dismiss or (text == 'OK' and not callback):
                    btn = MDRectangleFlatButton(
                        text=text,
                        on_release=lambda x, dlg=dialog: dlg.dismiss()
                    )
                else:
                    btn = MDRectangleFlatButton(
                        text=text,
                        on_release=lambda x, cb=callback: cb()
                    )
                buttons.append(btn)
            
            dialog.buttons = buttons
        
        dialog.open()
        return dialog
    
    # ========== ЮКЛАНИШ ==========
    def show_loading(self, message="Юкланмоқда..."):
        dialog = MDDialog(
            title="⏳ Илтимос кутинг",
            text=str(message),
            auto_dismiss=False
        )
        dialog.open()
        return dialog
    
    def hide_loading(self, dialog):
        if dialog:
            dialog.dismiss()
    
    # ========== МАТН КИРИТИШ ==========
    def show_input_dialog(self, title, hint_text, on_submit=None,
                          input_filter=None, default_text=""):
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.textfield import MDTextField
        
        content = MDBoxLayout(
            orientation='vertical',
            spacing=10,
            padding=20,
            size_hint_y=None,
            height=120
        )
        
        text_input = MDTextField(
            hint_text=hint_text,
            text=default_text,
            input_filter=input_filter,
            size_hint_y=None,
            height=48
        )
        content.add_widget(text_input)
        
        dialog = MDDialog(
            title=title,
            type="custom",
            content_cls=content,
        )
        
        dialog.buttons = [
            MDRectangleFlatButton(
                text="БЕКОР",
                on_release=lambda x, dlg=dialog: dlg.dismiss()
            ),
            MDRectangleFlatButton(
                text="OK",
                on_release=lambda x, dlg=dialog: self._handle_input(dlg, text_input.text, on_submit)
            )
        ]
        dialog.open()
    
    def _handle_input(self, dialog, value, callback):
        dialog.dismiss()
        if callback:
            callback(value)
    
    # ========== РЎЙХАТДАН ТАНЛАШ ==========
    def show_list_dialog(self, title, items, on_select=None):
        """Рўйхатдан танлаш диалоги"""
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.list import OneLineListItem
        from kivy.uix.scrollview import ScrollView
        from kivymd.uix.list import MDList
        
        content = MDBoxLayout(
            orientation='vertical',
            spacing=5,
            padding=10,
            size_hint_y=None,
            height=min(len(items) * 48 + 40, 400)
        )
        
        scroll = ScrollView()
        md_list = MDList()
        
        dialog = MDDialog(
            title=title,
            type="custom",
            content_cls=content,
        )
        
        for item in items:
            if isinstance(item, dict):
                text = item.get('text', '')
                value = item.get('value', item)
            else:
                text = str(item)
                value = item
            
            list_item = OneLineListItem(
                text=text,
                on_release=lambda x, v=value, dlg=dialog: self._handle_list_select(dlg, v, on_select)
            )
            md_list.add_widget(list_item)
        
        scroll.add_widget(md_list)
        content.add_widget(scroll)
        
        dialog.buttons = [
            MDRectangleFlatButton(
                text="БЕКОР",
                on_release=lambda x, dlg=dialog: dlg.dismiss()
            )
        ]
        dialog.open()
    
    def _handle_list_select(self, dialog, value, callback):
        dialog.dismiss()
        if callback:
            callback(value)