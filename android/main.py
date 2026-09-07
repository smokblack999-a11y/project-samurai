import os,requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.filechooser import FileChooserIconView
URL=os.getenv('STOCKSCAN_BACKEND_URL','http://10.0.2.2:8000')
TOKEN=os.getenv('STOCKSCAN_API_TOKEN','change-me')
class StockScanApp(App):
    def build(self):
        root=BoxLayout(orientation='vertical')
        root.add_widget(Label(text='StockScan Profit ULTRA'))
        chooser=FileChooserIconView(filters=['*.jpg','*.jpeg','*.png'])
        root.add_widget(chooser)
        button=Button(text='SCAN RECEIPT'); root.add_widget(button)
        result=Label(text='Choose receipt'); root.add_widget(result)
        def scan(_):
            if not chooser.selection:return
            path=chooser.selection[0]
            with open(path,'rb') as f:
                response=requests.post(URL+'/v1/receipts/extract',files={'file':(os.path.basename(path),f,'image/jpeg')},headers={'X-Stockscan-Token':TOKEN},timeout=90)
            result.text=response.text[:5000]
        button.bind(on_press=scan)
        return root
if __name__=='__main__': StockScanApp().run()
