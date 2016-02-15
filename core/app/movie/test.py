import filmDecrypter

data = "19040b43812aa0b65a6e15987cca71f34cee3d38419b070f91f5ae2df2f6e561444ec12f200be8f31deccaabcf47b33487c2c44a7946ed302eeee31b0612d88309b99426381fc342543e778c4df89e38119a1b39845eaaed665bbe2e0fc512df569104542b972ccfe7f3ac396c2270fd99575955f5854588bb0a1e32da452054"
key = "b1\x95\xcf\xa3\x94\xe5\x6c\x01\x5e\xcb\xda\xf1\x05\x3a\x6b\x39"

cryptor 	= filmDecrypter.filmDecrypter(198,128)
movie 		= cryptor.decrypt(data, key,'ECB').split('\0')[0]
print(movie)